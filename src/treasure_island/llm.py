"""The LLM brain: one model request per turn, and its reply back as a tool call.

A request holds only what a pirate needs: the system prompt, the turn's text,
the pirate's tools as function definitions, the reply cap, whether to think and
the budget for a model's own reasoning. It
goes through `Replies`, so it's stored, reused across runs and replayed without
a backend. A backend answers with JSON text: `{"tool": ..., "arguments": {...}}`,
plus `"thinking"` when thinking is on. Each backend turns its provider's tool
call into that one form.

Each backend says which way its models think (`backends.thinking_way`). A model
that reasons on its own gets `thinking_tokens` for it, even with thinking off,
since some providers reason whether asked or not, and what it returns is kept
when thinking is on; any other model, fakes included, is asked to write a short thought in its
answer, inside `reply_tokens`.

A reply that isn't a valid tool call, one the token limit cut off included, is kept for our record and comes back as a
failed action, so the game tells the pirate why and asks again, and after
`failed_tries` failed actions in one turn the turn passes.

Implements: treasure-island/old-scroll, treasure-island/end-report, treasure-island/retries-dropped-calls, agents/reasoning-looked-up, treasure-island/model-reasoning, agents/one-request-per-turn, agents/reply-is-a-tool-call, agents/ask-once-more, agents/reply-cap, agents/plays-then-replays, treasure-island/thinking, treasure-island/pluggable-pirate, treasure-island/model-backends, treasure-island/audit-record, treasure-island/private-report, treasure-island/free-talk, treasure-island/alert, treasure-island/go-to
"""

import json

from treasure_island.backends import thinking_way
from treasure_island.brain import (
    GO_TO,
    RANGED_READ,
    RECORD_TOOLS,
    REPORT_TOOLS,
    TALK_PARAMETERS,
    TOOLS,
    BadToolCall,
    Decision,
    tool_call,
)
from treasure_island.event_log import DIRECTIONS

_SCHEMAS = {
    "direction": {"type": "string", "enum": list(DIRECTIONS)},
    "turn": {
        "type": "integer",
        "description": "the turn's number, as your record shows it",
    },
    "start": {"type": "integer", "description": "the first line to read"},
    "end": {"type": "integer", "description": "the last line to read"},
    "alert": {"type": "boolean", "description": TALK_PARAMETERS["alert"]},
}


def _definition(tool):
    return {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": {
            "type": "object",
            "properties": {
                name: _SCHEMAS.get(name, {"type": "string", "description": text})
                for name, text in tool["parameters"].items()
            },
            # A ranged read may leave out both line numbers (`old-scroll`).
            "required": [] if tool is RANGED_READ else list(tool["parameters"]),
        },
    }


TOOL_DEFINITIONS = [_definition(tool) for tool in TOOLS]
RECORD_TOOL_DEFINITIONS = [_definition(tool) for tool in RECORD_TOOLS]
REPORT_TOOL_DEFINITIONS = [_definition(tool) for tool in REPORT_TOOLS]


RANGED_READ_DEFINITION = _definition(RANGED_READ)
GO_TO_DEFINITION = _definition(GO_TO)  # offered only with `go_to` on (`go-to`)


def tools_for(config):
    """The tools a pirate is offered: the record's two and the private report's as
    well only when each is on, and `read` with a start and an end only with the old
    scroll on."""
    offered = TOOL_DEFINITIONS
    if config.old_scroll:
        offered = [
            RANGED_READ_DEFINITION if tool["name"] == "read" else tool
            for tool in offered
        ]
    if config.go_to:
        offered = [*offered, GO_TO_DEFINITION]
    if config.audit_record or config.private_report:
        offered = [
            *offered,
            *(RECORD_TOOL_DEFINITIONS if config.audit_record else []),
            *(REPORT_TOOL_DEFINITIONS if config.private_report else []),
        ]
    return [_talking(tool) for tool in offered] if config.free_talk else offered


def _talking(definition):
    """A tool's definition, also taking an optional message and alert (`free-talk`)."""
    parameters = definition["parameters"]
    talk = {
        name: _SCHEMAS.get(name, {"type": "string", "description": text})
        for name, text in TALK_PARAMETERS.items()
    }
    return {
        **definition,
        "parameters": {
            **parameters,
            "properties": {**parameters["properties"], **talk},
        },
    }


# Asked of a model that doesn't reason on its own, when thinking is on.
THOUGHT = (
    "Think before you act: put a short thought, a sentence or two, in your "
    'answer as "thinking", beside your tool call.'
)


def _reasoning_tokens(text):
    """The reasoning tokens a backend says a reply spent, or None."""
    try:
        reply = json.loads(text)
    except json.JSONDecodeError:
        return None
    spent = reply.get("reasoning_tokens") if isinstance(reply, dict) else None
    return spent if isinstance(spent, int) and not isinstance(spent, bool) else None


def _read_reply(text, ranged=False, free_talk=False):
    """The tool call in a reply and its thinking, or BadToolCall saying why not."""
    try:
        reply = json.loads(text)
    except json.JSONDecodeError:
        raise BadToolCall("your answer wasn't JSON naming a tool") from None
    if isinstance(reply, dict) and reply.get("cut_off") is True:
        raise BadToolCall(
            "your answer ran out of room at the token limit before it named a "
            "tool: think less and answer with a tool call"
        )
    if not isinstance(reply, dict) or "tool" not in reply or "arguments" not in reply:
        raise BadToolCall('your answer needs "tool" and "arguments"')
    action = tool_call(reply["tool"], reply["arguments"], ranged, free_talk)
    return action, reply.get("thinking")


class LLMPirate:
    """A brain that asks a model, through stored replies, for each try at a turn."""

    def __init__(self, name, pirate, replies, config):
        """`pirate` is its config entry: the model it plays and how it thinks."""
        self._name = name
        self._model = pirate.model
        self._replies = replies
        self._config = config
        self._built_in = thinking_way(pirate.model, pirate.thinks) == "built-in"

    def _request(self, view):
        thinking = self._config.thinking
        turn = view.turn_text()
        if thinking and not self._built_in:
            turn += f"\n\n{THOUGHT}"
        return {
            "agent": self._name,
            "model": self._model,
            "seed": self._config.seed,
            "system": view.system_prompt,
            "messages": [{"role": "user", "content": turn}],
            "tools": tools_for(self._config),
            "max_tokens": self._config.reply_tokens,
            "thinking": thinking,
            # Some providers reason whether asked or not, so a model that
            # reasons gets its budget even with thinking off.
            "thinking_tokens": self._config.thinking_tokens if self._built_in else 0,
        }

    def note(self, system, text):
        """A free-text answer with no tools: the end report's note, cached like a turn."""
        request = {
            "agent": self._name,
            "model": self._model,
            "seed": self._config.seed,
            "system": system,
            "messages": [{"role": "user", "content": text}],
            "tools": [],
            "max_tokens": self._config.reply_tokens,
            "thinking": self._config.thinking,
            "thinking_tokens": self._config.thinking_tokens if self._built_in else 0,
        }
        return self._replies.ask(request).strip()

    def decide(self, view):
        text = self._replies.ask(self._request(view))
        retried = self._replies.last_retries
        spent = _reasoning_tokens(text)
        try:
            action, thinking = _read_reply(
                text, self._config.old_scroll, self._config.free_talk
            )
        except BadToolCall as why:
            # A failed action: the game tells the pirate why and asks again.
            bad = ({"reply": text, "why": str(why)},)
            return Decision(None, None, bad, retried, spent)
        kept = thinking if self._config.thinking and thinking else None
        return Decision(action, kept, (), retried, spent)
