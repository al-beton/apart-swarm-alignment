"""OpenRouter's chat completions, as a backend: `openrouter/<model id>`.

One request asks the model for one of the pirate's tools. Its tool call comes back in
the one reply form the LLM brain reads, `{"tool": ..., "arguments": {...}}`, with
`"thinking"` when thinking is on. A reply with no tool call is passed on as its
text, so the brain records why it's refused and asks once more. The cost is the
reply's own `usage.cost`; OpenRouter's credits are dollars (default, Al to confirm).
A reply with no cost stops the game, since the spending cap couldn't count it.

Default, Al to confirm: the model may answer without a tool (`tool_choice` "auto"),
since some models refuse to be forced, and thinking off sends no reasoning setting,
so each model reasons as it does by default and its reasoning isn't kept. Thinking
on asks for reasoning within `thinking_tokens`, on top of the reply's cap.

`OpenRouter.check_key` asks OpenRouter about a key, not a model, so it spends nothing.
It never says the key's `label`, since OpenRouter's label is the key, masked.

Implements: agents/reasoning-looked-up, treasure-island/model-reasoning, agents/openrouter-backend, agents/check-keys, agents/normal-temperature
"""

import json
import urllib.error
import urllib.request

from treasure_island.game_loop import GameStopped

URL = "https://openrouter.ai/api/v1/chat/completions"
KEY_URL = "https://openrouter.ai/api/v1/key"
MODELS_URL = "https://openrouter.ai/api/v1/models"  # free, and needs no key
TIMEOUT_SECONDS = 120


def _body(model_id, request):
    body = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": request["system"]},
            *request["messages"],
        ],
        "tools": [{"type": "function", "function": tool} for tool in request["tools"]],
        "tool_choice": "auto",
        "max_tokens": request["max_tokens"] + request["thinking_tokens"],
        "seed": request["seed"],
    }
    if request["thinking"] and request["thinking_tokens"]:
        # The reasoning's own budget, on top of the reply's; a model that writes
        # its thought in its reply has none, and is sent no reasoning setting.
        body["reasoning"] = {"max_tokens": request["thinking_tokens"]}
    return body


def thinks_for(model_id):
    """ "built-in" if OpenRouter's listing says this model reasons, "in-reply" if
    it says it doesn't, or None if the listing can't be read or doesn't list it."""
    try:
        with urllib.request.urlopen(MODELS_URL, timeout=TIMEOUT_SECONDS) as answer:
            listing = json.load(answer)["data"]
    except (urllib.error.URLError, OSError, ValueError, KeyError, TypeError):
        return None
    for entry in listing:
        if entry.get("id") == model_id:
            reasons = "reasoning" in (entry.get("supported_parameters") or [])
            return "built-in" if reasons else "in-reply"
    return None


def _reply_text(message, thinking):
    """The reply in the brain's one form, or the model's own words if it called no tool."""
    calls = message.get("tool_calls") or []
    if not calls:
        return message.get("content") or ""
    function = calls[0]["function"]
    try:
        arguments = json.loads(function.get("arguments") or "{}")
    except json.JSONDecodeError:
        arguments = function["arguments"]  # the brain says what's wrong with it
    reply = {"tool": function.get("name"), "arguments": arguments}
    if thinking and message.get("reasoning"):
        reply["thinking"] = message["reasoning"]
    return json.dumps(reply)


class OpenRouter:
    THINKS = "built-in"  # its models' own reasoning, where they return it
    """A backend for one OpenRouter model: `backend(request)` -> (text, cost)."""

    def __init__(self, model_id, key):
        self.model_id = model_id
        self._key = key

    def __call__(self, request):
        sent = urllib.request.Request(
            URL,
            data=json.dumps(_body(self.model_id, request)).encode(),
            headers={
                "Authorization": f"Bearer {self._key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(sent, timeout=TIMEOUT_SECONDS) as answer:
            reply = json.load(answer)
        cost = (reply.get("usage") or {}).get("cost")
        if not isinstance(cost, (int, float)):
            raise GameStopped(
                f"OpenRouter's reply for {self.model_id} gave no cost, "
                "so the spending cap couldn't count it"
            )
        text = _reply_text(reply["choices"][0]["message"], request["thinking"])
        return text, float(cost)

    @staticmethod
    def check_key(key):
        """Whether OpenRouter takes this key, and what it says the key has spent."""
        asked = urllib.request.Request(
            KEY_URL, headers={"Authorization": f"Bearer {key}"}, method="GET"
        )
        try:
            with urllib.request.urlopen(asked, timeout=TIMEOUT_SECONDS) as answer:
                data = json.load(answer)["data"]
        except urllib.error.HTTPError as refused:
            if refused.code in (401, 403):
                return (
                    False,
                    f"is set, but OpenRouter rejected it (HTTP {refused.code}).",
                )
            return (
                False,
                f"couldn't be checked: OpenRouter answered HTTP {refused.code}.",
            )
        except (urllib.error.URLError, OSError, ValueError, KeyError) as why:
            return False, f"couldn't be checked: {type(why).__name__}."
        spent = f"it has spent ${data.get('usage') or 0:.2f}"
        if data.get("limit") is None:
            return True, f"works; {spent}, with no limit on the key."
        left = data.get("limit_remaining")
        rest = f" (${left:.2f} left)" if isinstance(left, (int, float)) else ""
        return True, f"works; {spent} of its ${data['limit']:.2f} limit{rest}."
