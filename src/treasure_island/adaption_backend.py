"""The Adaption backend: hosted open models, paid for with Adaption credits.

A model named `adaption/<model id>` goes to Adaption's Responses API through its
`adaption` SDK, the only way its docs show to call a model. The request carries
the rules as instructions, the turn's messages as input, the pirate's tools
as function tools and the reply cap. The first function call in the reply becomes
the JSON the LLM brain reads; a reply with no function call comes back as its
words, so the brain can say why and ask once more.

A reply costs its token usage at the model's rate in `RATES`, in credits per
million tokens, from Adaption's price list (its model listing has no prices). A
model with no rate is refused rather than run unpriced, and a reply that gives no
token usage stops the run, since the spending cap couldn't count it. Default, Al to confirm:
a credit counts as a dollar, so the manifest's `cost_usd` totals credits.

`check_key` lists the hosted models the key can use, which asks no model anything
and spends nothing. `backends` makes one for each run, with the key from `ADAPTION_API_KEY`, and the
key goes only to the SDK's client, so it never reaches a request, a reply or a
run folder.

Implements: agents/adaption-backend, agents/adaption-cost, agents/check-keys
"""

import json

from treasure_island.game_loop import GameStopped

# Model id -> (credits per million input tokens, credits per million output tokens).
RATES = {"deepseek-v4-flash": (0.044, 0.133)}


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


def _reply_text(response, thinking):
    """The JSON the LLM brain reads, or the reply's own words if it called no tool."""
    calls = [item for item in response.output if item.type == "function_call"]
    if not calls:
        return response.output_text
    call = calls[0]
    try:
        arguments = json.loads(call.arguments or "{}")
    except json.JSONDecodeError:
        arguments = call.arguments
    reply = {"tool": call.name, "arguments": arguments}
    reasoning = [
        part.get("text", "")
        for item in response.output
        if item.type == "reasoning"
        for part in item.summary or []
    ]
    if thinking and any(reasoning):
        reply["thinking"] = " ".join(text for text in reasoning if text)
    return json.dumps(reply)


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
            max_output_tokens=request["max_tokens"],
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
