"""The LLM brain: one model request per turn, and its reply back as a tool call.

A request holds only what a pirate needs: the system prompt, the turn's text,
the four tools as function definitions, the reply cap and whether to think. It
goes through `Replies`, so it's stored, reused across runs and replayed without
a backend. A backend answers with JSON text: `{"tool": ..., "arguments": {...}}`,
plus `"thinking"` when thinking is on. Each backend turns its provider's tool
call into that one form.

A reply that isn't a valid tool call is kept for our record, and the pirate is
told why and asked once more. If that answer is no good either, the turn passes
with no action (default, Al to confirm).

Implements: agents/one-request-per-turn, agents/reply-is-a-tool-call, agents/ask-once-more, agents/reply-cap, agents/plays-then-replays, treasure-island/thinking, treasure-island/pluggable-pirate, treasure-island/model-backends
"""

import json

from treasure_island.brain import TOOLS, BadToolCall, Decision, tool_call
from treasure_island.event_log import DIRECTIONS

_SCHEMAS = {"direction": {"type": "string", "enum": list(DIRECTIONS)}}

TOOL_DEFINITIONS = [
    {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": {
            "type": "object",
            "properties": {
                name: _SCHEMAS.get(name, {"type": "string", "description": text})
                for name, text in tool["parameters"].items()
            },
            "required": list(tool["parameters"]),
        },
    }
    for tool in TOOLS
]
ASKS = 2  # the first request, and once more after a reply that wasn't a tool call


def _read_reply(text):
    """The tool call in a reply and its thinking, or BadToolCall saying why not."""
    try:
        reply = json.loads(text)
    except json.JSONDecodeError:
        raise BadToolCall("your answer wasn't JSON naming a tool") from None
    if not isinstance(reply, dict) or "tool" not in reply or "arguments" not in reply:
        raise BadToolCall('your answer needs "tool" and "arguments"')
    return tool_call(reply["tool"], reply["arguments"]), reply.get("thinking")


class LLMPirate:
    """A brain that asks a model, through stored replies, for each turn's action."""

    def __init__(self, name, model, replies, config):
        self._name = name
        self._model = model
        self._replies = replies
        self._config = config

    def _request(self, view, messages):
        return {
            "agent": self._name,
            "model": self._model,
            "seed": self._config.seed,
            "system": view.system_prompt,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "max_tokens": self._config.reply_tokens,
            "thinking": self._config.thinking,
        }

    def decide(self, view):
        messages = [{"role": "user", "content": view.turn_text()}]
        refused = []
        for _ in range(ASKS):
            text = self._replies.ask(self._request(view, messages))
            try:
                action, thinking = _read_reply(text)
            except BadToolCall as why:
                refused.append({"reply": text, "why": str(why)})
                messages = [
                    *messages,
                    {"role": "assistant", "content": text},
                    {
                        "role": "user",
                        "content": f"That isn't a tool call you can make: {why}. "
                        "Answer with exactly one of the four tools.",
                    },
                ]
                continue
            kept = thinking if self._config.thinking and thinking else None
            return Decision(action, kept, tuple(refused))
        return Decision(None, None, tuple(refused))
