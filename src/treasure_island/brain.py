"""How a pirate's brain plugs in: what it's shown each turn and how it answers.

A brain is anything with `decide(view) -> Decision`: a scripted strategy reads
the view's fields, and an LLM reads `view.as_text()`. Either way it answers
with one of four tool calls, in the same form the event log records.

The game gives each pirate a `PirateSeat`, which builds the view and keeps that
pirate's own memory. A seat is only ever handed what the pirate may know: its
position and its turns left, and later what each of its reads found on the
scroll. So other pirates and the treasure can't reach a brain, and neither can
another pirate's thinking. Nothing on the scroll is shown for free.

Implements: treasure-island/pluggable-pirate, treasure-island/tools-only, treasure-island/turn-view, treasure-island/no-vision, treasure-island/agent-memory, treasure-island/thinking, treasure-island/what-they-are-told, treasure-island/looks-are-cosmetic
"""

import dataclasses
import json
from typing import Protocol

from treasure_island.event_log import DIRECTIONS, is_action

TOOLS = (
    {
        "name": "move",
        "description": "Walk one square. A move off the grid fails and uses your turn.",
        "parameters": {"direction": f"one of {', '.join(DIRECTIONS)}"},
    },
    {
        "name": "dig",
        "description": "Dig your square, which is also how you search it.",
        "parameters": {},
    },
    {
        "name": "write",
        "description": "Write a note on the scroll, the only way to reach the other pirates.",
        "parameters": {"text": "your note, on one line"},
    },
    {
        "name": "read",
        "description": "Read every line on the scroll you haven't read yet.",
        "parameters": {},
    },
)
_PARAMETERS = {tool["name"]: set(tool["parameters"]) for tool in TOOLS}
TOOL_HELP = {
    tool["name"]: ", ".join(f"{k} must be {v}" for k, v in tool["parameters"].items())
    for tool in TOOLS
}


class BadToolCall(ValueError):
    """An answer that isn't one of the four tool calls. The message says why."""


def tool_call(name, arguments):
    """The event-log action for a tool call, or BadToolCall saying what's wrong."""
    described = f"{name}({json.dumps(arguments)})"
    if name not in _PARAMETERS:
        raise BadToolCall(f"{described}: the tools are {', '.join(_PARAMETERS)}")
    if not isinstance(arguments, dict) or set(arguments) != _PARAMETERS[name]:
        raise BadToolCall(f"{described}: {name} takes {sorted(_PARAMETERS[name])}")
    action = {"action": name, **arguments}
    if not is_action(action):
        raise BadToolCall(f"{described}: {TOOL_HELP[name]}")
    return action


def system_prompt(config):
    """The rules and actions. Pirates' looks are cosmetic, so they aren't here."""
    tools = "\n".join(
        f"- {tool['name']}: {tool['description']}"
        + (f" ({TOOL_HELP[tool['name']]})" if tool["parameters"] else "")
        for tool in TOOLS
    )
    return (
        "This is a study of how well a swarm of agents works together, "
        "and your crew is scored.\n"
        f"You are one of {config.crew_size} pirates digging for one buried treasure "
        f"on a {config.grid_size} by {config.grid_size} grid. Each pirate gets "
        f"{config.turns_per_pirate} turns. Your crew does best if everyone stands on "
        "the treasure once it has been dug up, with moves to spare.\n"
        "You can't see the grid or the other pirates. You know only your own "
        "position and what you have dug. The scroll is the only way to reach the "
        "others, and nothing on it is shown to you for free. Writing adds one line "
        "with your name on it. Reading shows you everything new that the others "
        "have written since you last read, each line with who wrote it. "
        "Writing and reading each use your turn.\n"
        f"Each turn is exactly one action:\n{tools}"
    )


def _scroll_text(lines):
    return " | ".join(
        f"line {line['line']} by {line['by']}: {line['text']}" for line in lines
    )


@dataclasses.dataclass(frozen=True)
class EarlierTurn:
    """One of a pirate's own earlier turns, including the lines a read found."""

    position: tuple
    action: dict
    result: str
    thinking: str | None = None
    read_lines: list = dataclasses.field(default_factory=list)

    def as_text(self):
        step = " ".join(str(part) for part in self.action.values())
        thought = f" You were thinking: {self.thinking}" if self.thinking else ""
        found = f" It said: {_scroll_text(self.read_lines)}." if self.read_lines else ""
        return f"- At {self.position}. You did: {step}. {self.result}{found}{thought}"


@dataclasses.dataclass(frozen=True)
class TurnView:
    """Everything a pirate is shown. It has no field for anything else."""

    name: str
    system_prompt: str
    position: tuple
    turns_left: int
    earlier_turns: tuple

    def as_text(self):
        """The whole view as plain words, which is what an LLM reads."""
        earlier = [turn.as_text() for turn in self.earlier_turns]
        now = f"You are {self.name}, at {self.position}, "
        now += f"with {self.turns_left} turns left."
        return "\n\n".join(
            [
                self.system_prompt,
                "Your earlier turns:\n" + ("\n".join(earlier) or "None yet."),
                now,
            ]
        )


@dataclasses.dataclass(frozen=True)
class Decision:
    """A brain's answer. `thinking` is optional, for our record only."""

    action: dict
    thinking: str | None = None


class Brain(Protocol):
    def decide(self, view: TurnView) -> Decision: ...


class PirateSeat:
    """One pirate at the table: its brain and its own memory."""

    def __init__(self, name, brain, config):
        self._name = name
        self._brain = brain
        self._prompt = system_prompt(config)
        self._earlier = ()
        self._pending = None

    def take_turn(self, position, turns_left):
        """Ask the brain for this turn's decision, checking it's a real tool call."""
        view = TurnView(self._name, self._prompt, position, turns_left, self._earlier)
        decision = self._brain.decide(view)
        if not is_action(decision.action):
            raise BadToolCall(f"{json.dumps(decision.action)} is not a tool call")
        self._pending = (position, decision)
        return decision

    def remember(self, result, read_lines=()):
        """Tell the pirate what its last action did, and any lines its read found."""
        position, decision = self._pending
        earlier = EarlierTurn(
            position, decision.action, result, decision.thinking, list(read_lines)
        )
        self._earlier = (*self._earlier, earlier)
