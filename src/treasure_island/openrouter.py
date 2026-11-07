"""OpenRouter's chat completions, as a backend: `openrouter/<model id>`.

One request asks the model for one of the four tools. Its tool call comes back in
the one reply form the LLM brain reads, `{"tool": ..., "arguments": {...}}`, with
`"thinking"` when thinking is on. A reply with no tool call is passed on as its
text, so the brain records why it's refused and asks once more. The cost is the
reply's own `usage.cost`; OpenRouter's credits are dollars (default, Al to confirm).
A reply with no cost stops the game, since the spending cap couldn't count it.

Default, Al to confirm: the model may answer without a tool (`tool_choice` "auto"),
since some models refuse to be forced, and thinking off sends no reasoning setting,
so each model reasons as it does by default and its reasoning isn't kept.

Implements: agents/openrouter-backend
"""

import json
import urllib.request

from treasure_island.game_loop import GameStopped

URL = "https://openrouter.ai/api/v1/chat/completions"
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
        "max_tokens": request["max_tokens"],
        "seed": request["seed"],
    }
    if request["thinking"]:
        body["reasoning"] = {"enabled": True}
    return body


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
