"""How a pirate's brain plugs in: what it's shown each turn and how it answers.

A brain is anything with `decide(view) -> Decision`: a scripted strategy reads
the view's fields, and an LLM reads `view.as_text()`. Either way it answers
with one of four tool calls, in the same form the event log records.

The game gives each pirate a `PirateSeat`, which builds the view and keeps that
pirate's own memory. A seat is only ever handed what the pirate may know: its
position, its turns left and the log lines it may see. So other pirates and the
treasure can't reach a brain, and neither can another pirate's thinking.

Implements: treasure-island/pluggable-pirate, treasure-island/tools-only, treasure-island/turn-view, treasure-island/no-vision, treasure-island/agent-memory, treasure-island/thinking, treasure-island/what-they-are-told
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
        "description": "Add a note to the log, the only way to reach the other pirates.",
        "parameters": {"text": "your note, on one line"},
    },
    {
        "name": "read",
        "description": "Read the lines around a line number further back in the log.",
        "parameters": {"line": "a line number"},
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
        "position and what you have dug. The log is the only way to reach the others: "
        f"each turn you are shown its last {config.log_window} lines, and reading "
        f"further back shows {config.read_size} lines and uses your turn. "
        "Every turn adds a line to the log, blank unless that turn wrote a note.\n"
        f"Each turn is exactly one action:\n{tools}"
    )


@dataclasses.dataclass(frozen=True)
class EarlierTurn:
    """One of a pirate's own earlier turns, as it remembers it."""

    position: tuple
    action: dict
    result: str
    thinking: str | None = None

    def as_text(self):
        step = " ".join(str(part) for part in self.action.values())
        thought = f" You were thinking: {self.thinking}" if self.thinking else ""
        return f"- At {self.position} you did: {step}. {self.result}{thought}"


@dataclasses.dataclass(frozen=True)
class TurnView:
    """Everything a pirate is shown. It has no field for anything else."""

    name: str
    system_prompt: str
    position: tuple
    turns_left: int
    log_lines: list
    earlier_turns: tuple

    def as_text(self):
        """The whole view as plain words, which is what an LLM reads."""
        log = [
            f"{line['line']}: {line['text'] or '(blank)'}" for line in self.log_lines
        ]
        earlier = [turn.as_text() for turn in self.earlier_turns]
        now = f"You are {self.name}, at {self.position}, "
        now += f"with {self.turns_left} turns left."
        return "\n\n".join(
            [
                self.system_prompt,
                "Your earlier turns:\n" + ("\n".join(earlier) or "None yet."),
                "The log's latest lines:\n" + ("\n".join(log) or "The log is empty."),
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

    def take_turn(self, position, turns_left, log_lines):
        """Ask the brain for this turn's decision, checking it's a real tool call."""
        view = TurnView(
            self._name,
            self._prompt,
            position,
            turns_left,
            log_lines,
            self._earlier,
        )
        decision = self._brain.decide(view)
        if not is_action(decision.action):
            raise BadToolCall(f"{json.dumps(decision.action)} is not a tool call")
        self._pending = (position, decision)
        return decision

    def remember(self, result):
        """Tell the pirate what its last action did, for its later turns."""
        position, decision = self._pending
        earlier = EarlierTurn(position, decision.action, result, decision.thinking)
        self._earlier = (*self._earlier, earlier)
