"""The Adaption backend: hosted open models, paid for with Adaption credits.

A model named `adaption/<model id>` goes to Adaption's Responses API through its
`adaption` SDK, the only way its docs show to call a model. The request carries
the rules as instructions, the turn's messages as input, the pirate's tools
as function tools and the reply cap. The first function call in the reply becomes
the JSON the LLM brain reads; a reply with no function call comes back as its
words, so the brain can say why and ask once more, and one the token limit cut off
(`incomplete_details` "max_output_tokens") is marked so, keeping any reasoning
that came back when thinking is on.

A reply costs its token usage at the model's rate in `RATES`, in credits per
million tokens, from Adaption's price list (its model listing has no prices). A
model with no rate is refused rather than run unpriced, and a reply that gives no
token usage stops the run, since the spending cap couldn't count it. The manifest
totals credits as `cost_credits`, apart from dollars; the cap counts a credit as a
dollar (default, Al to confirm).

`check_key` lists the hosted models the key can use, which asks no model anything
and spends nothing. `backends` makes one for each run, with the key from `ADAPTION_API_KEY`, and the
key goes only to the SDK's client, so it never reaches a request, a reply or a
run folder.

Implements: treasure-island/model-reasoning, agents/adaption-backend, agents/adaption-cost, agents/check-keys, agents/normal-temperature, agents/reply-cap
"""

import json

from treasure_island.brain import cut_off_reply
from treasure_island.game_loop import GameStopped

# Model id -> (credits per million input tokens, credits per million output tokens).
RATES = {"deepseek-v4-flash": (0.044, 0.133)}
THINKS = "built-in"  # its models' own reasoning, returned as summaries or content


def client(key):
    """The SDK's client for this key. The SDK loads only when a run needs it."""
    import adaption

    return adaption.Adaption(api_key=key)


def check_key(key):
    """Whether Adaption takes this key, and how many hosted models it can use."""
    import adaption

    try:
        hosted = client(key).models.list(type="hosted")
    except adaption.APIStatusError as refused:
        if refused.status_code in (401, 403):
            return (
                False,
                f"is set, but Adaption rejected it (HTTP {refused.status_code}).",
            )
        return (
            False,
            f"couldn't be checked: Adaption answered HTTP {refused.status_code}.",
        )
    except (adaption.APIError, OSError) as why:
        return False, f"couldn't be checked: {type(why).__name__}."
    ids = [model.id for model in hosted.data]
    priced = sum(1 for model_id in ids if model_id in RATES)
    return True, (
        f"works; it can use {len(ids)} hosted models, {priced} of them priced here."
    )


def _text(part):
    # The SDK hands parts over as plain dicts or as typed objects.
    return (
        part.get("text") if isinstance(part, dict) else getattr(part, "text", "")
    ) or ""


def reasoning_tokens(response):
    """The reasoning tokens a reply spent, as its usage says, or None if it doesn't."""
    details = getattr(getattr(response, "usage", None), "output_tokens_details", None)
    if isinstance(details, dict):  # the SDK hands some parts over as plain dicts
        return details.get("reasoning_tokens")
    return getattr(details, "reasoning_tokens", None)


def _reply_text(response, thinking):
    """The JSON the LLM brain reads, or the reply's own words if it called no tool."""
    calls = [item for item in response.output if item.type == "function_call"]
    details = getattr(response, "incomplete_details", None)
    spent = reasoning_tokens(response)
    thought = _reasoning(response) if thinking else None
    if not calls and getattr(details, "reason", None) == "max_output_tokens":
        return cut_off_reply(response.output_text, spent, thought)
    if not calls:
        return response.output_text
    call = calls[0]
    try:
        arguments = json.loads(call.arguments or "{}")
    except json.JSONDecodeError:
        arguments = call.arguments
    reply = {"tool": call.name, "arguments": arguments}
    if spent is not None:
        reply["reasoning_tokens"] = spent
    if thought:
        reply["thinking"] = thought
    return json.dumps(reply)


def _reasoning(response):
    """The reasoning a reply returned, joined into one text, or None."""
    # deepseek's reasoning comes back as `reasoning_text` parts in `content`, with
    # an empty summary; a model that summarises puts its words in `summary`.
    reasoning = [
        _text(part)
        for item in response.output
        if item.type == "reasoning"
        for part in [*(item.summary or []), *(getattr(item, "content", None) or [])]
    ]
    return " ".join(text for text in reasoning if text) or None


class AdaptionBackend:
    def __init__(self, model_id, client):
        self._model = model_id
        self._client = client

    def __call__(self, request):
        response = self._client.responses.create(
            model=self._model,
            instructions=request["system"],
            input=request["messages"],
            tools=[{"type": "function", **tool} for tool in request["tools"]],
            # The Responses API counts reasoning as output, so its budget adds on;
            # the prompt tells the model less (`thinking_said`), so it has room.
            max_output_tokens=request["max_tokens"] + request["thinking_tokens"],
        )
        usage = response.usage
        if usage is None:
            raise GameStopped(
                f"Adaption's reply for {self._model} gave no token usage, "
                "so the spending cap couldn't count it"
            )
        per_input, per_output = RATES[self._model]
        cost = (usage.input_tokens * per_input + usage.output_tokens * per_output) / (
            1_000_000
        )
        return _reply_text(response, request["thinking"]), cost
