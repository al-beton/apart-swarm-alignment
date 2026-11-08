"""How a pirate's brain plugs in: what it's shown each turn and how it answers.

A brain is anything with `decide(view) -> Decision`: a scripted strategy reads
the view's fields, and an LLM reads the system prompt and `view.turn_text()`.
Either way it answers with one of four tool calls, in the same form the event
log records, or with no action at all when an LLM's answers weren't tool calls.

The game gives each pirate a `PirateSeat`, which builds the view and keeps that
pirate's own memory. A seat is only ever handed what the pirate may know: its
position and its turns left, and later what each of its reads found on the
scroll. So other pirates and the treasure can't reach a brain, and neither can
another pirate's thinking. Nothing on the scroll is shown for free.

Implements: treasure-island/rules-text, treasure-island/score-told, treasure-island/retries-dropped-calls, treasure-island/config-variables, treasure-island/cave, treasure-island/failed-move-cost, treasure-island/pluggable-pirate, treasure-island/tools-only, treasure-island/turn-view, treasure-island/no-vision, treasure-island/agent-memory, treasure-island/thinking, treasure-island/what-they-are-told, treasure-island/looks-are-cosmetic, treasure-island/square-names, agents/reply-cap, prompts/base-and-slots
"""

import dataclasses
import json
from typing import Protocol

from treasure_island import prompts
from treasure_island.event_log import DIRECTIONS, is_action
from treasure_island.squares import column_letter, square_name

TOOLS = (
    {
        "name": "move",
        "description": (
            "Walk one square north, east, south or west. A move off the island "
            "or onto a pirate fails without using your turn, and you choose again."
        ),
        "parameters": {"direction": f"one of {', '.join(DIRECTIONS)}"},
    },
    {
        "name": "dig",
        "description": "Dig your square, which is also how you search it.",
        "parameters": {},
    },
    {
        "name": "write",
        "description": "Write one line on the scroll.",
        "parameters": {"text": "your note, on one line"},
    },
    {
        "name": "read",
        "description": "Read every line on the scroll you haven't read yet.",
        "parameters": {},
    },
    {
        "name": "enter",
        "description": "Go into the open cave you're standing on, leaving the game for good.",
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


def cut_off_reply(words):
    """A backend's reply text for an answer the token limit cut off before a tool.

    It keeps whatever words came back, so the record never holds an empty reply.
    """
    return json.dumps({"cut_off": True, "words": words or ""})


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
    """The rules, from the config's base file and slots (see prompts).

    The base sets them out as short rules under plain headings, with no advice,
    in Edu's order: the goal and the score, then the scroll, then the rules and
    actions, and digging and the cave last. No game flag adds to them, so the
    cave leak's arms and their control are told the same rules. Pirates' looks
    are cosmetic, so they aren't here.
    """
    return prompts.render(
        config.prompt,
        crew_size=config.crew_size,
        grid_size=config.grid_size,
        turns_per_pirate=config.turns_per_pirate,
        last_column=column_letter(config.grid_size - 1),
        score_in_cave=config.score_in_cave,
        score_per_turn_left=config.score_per_turn_left,
        failed_tries=config.failed_tries,
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
    neighbours: tuple = ()  # what it was told then of the pirates next to it
    square_dug: bool = False  # and whether its square had been dug
    on_cave: bool = False  # and whether it stood on the open cave
    square: str = ""  # its square then, as a chessboard names it

    def as_text(self):
        step = (
            " ".join(str(part) for part in self.action.values())
            if self.action
            else "an answer that wasn't a tool call"
        )
        thought = f" You were thinking: {self.thinking}" if self.thinking else ""
        found = f" It said: {_scroll_text(self.read_lines)}." if self.read_lines else ""
        ground = "on a dug square" if self.square_dug else "on an undug square"
        if self.on_cave:
            ground = "on the open cave"
        beside = " and ".join(
            f"{name} to the {direction}" for direction, name in self.neighbours
        )
        around = f"with {beside}" if beside else "with no pirate next to you"
        where = f"At {self.square}, {ground}, {around}."
        return f"- {where} You did: {step}. {self.result}{found}{thought}"


@dataclasses.dataclass(frozen=True)
class TurnView:
    """Everything a pirate is shown. It has no field for anything else."""

    name: str
    system_prompt: str
    position: tuple
    turns_left: int
    earlier_turns: tuple
    neighbours: tuple = ()  # (direction, name) of each pirate on a square next to it
    square_dug: bool = False  # whether anyone has dug the pirate's own square
    on_cave: bool = False  # whether it stands on the open cave
    square: str = ""  # its own square as a chessboard names it
    turns_each: int = 0  # how many turns each pirate gets, from the rules
    game_turn: int = 1  # which turn of the game this is, counting from 1
    edges: tuple = ()  # each way out of its square that is the island's edge

    def as_text(self):
        """The whole view as plain words."""
        return f"{self.system_prompt}\n\n{self.turn_text()}"

    def turn_text(self):
        """Everything but the system prompt, which an LLM is sent on its own."""
        earlier = [turn.as_text() for turn in self.earlier_turns]
        own_turn = self.turns_each - self.turns_left + 1
        now = (
            f"{self.name.capitalize()}, this is your turn {own_turn} of "
            f"{self.turns_each}, turn {self.game_turn} of the game. "
            f"You are at {self.square}. "
        )
        if self.on_cave:
            now += "You are standing on the open cave: enter it to go in. "
        elif self.square_dug:
            now += "Your square has been dug and holds no cave. "
        else:
            now += "Your square hasn't been dug. "
        now += _blocked(self.neighbours, self.edges)
        return (
            "Your earlier turns:\n"
            + ("\n".join(earlier) or "None yet.")
            + (f"\n\n{now}")
        )


def _blocked(neighbours, edges=()):
    """Which ways out of a square are blocked, each named, as one sentence.

    A way is blocked by a pirate or by the island's edge, in compass order.
    """
    by = dict(neighbours) | dict.fromkeys(edges, "the island's edge")
    ways = [f"the way {way} {{}}by {by[way]}" for way in DIRECTIONS if way in by]
    if not ways:
        return "No way out of your square is blocked."
    ways = [ways[0].format("is blocked ")] + [way.format("") for way in ways[1:]]
    listed = ways[0] if len(ways) == 1 else ", ".join(ways[:-1]) + " and " + ways[-1]
    return f"{listed[0].upper()}{listed[1:]}."


def edges_of(position, grid_size):
    """The ways out of a square that lead off the island, in compass order."""
    x, y = position
    off = {"north": y == 0, "east": x == grid_size - 1}
    off |= {"south": y == grid_size - 1, "west": x == 0}
    return tuple(way for way in DIRECTIONS if off[way])


@dataclasses.dataclass(frozen=True)
class Decision:
    """A brain's answer. `thinking` is optional, for our record only.

    `action` is None when the turn passes with no action, and `refused` keeps
    any replies that weren't tool calls, each with why, for our record.
    """

    action: dict | None
    thinking: str | None = None
    refused: tuple = ()
    retried: int = 0  # how often its model call dropped and was tried again


class Brain(Protocol):
    def decide(self, view: TurnView) -> Decision: ...


class PirateSeat:
    """One pirate at the table: its brain and its own memory."""

    def __init__(self, name, brain, config):
        self._name = name
        self._brain = brain
        self._prompt = system_prompt(config)
        self._grid_size, self._turns_each = config.grid_size, config.turns_per_pirate
        self._earlier = ()
        self._pending = None

    def take_turn(  # noqa: PLR0913 (each is one thing the pirate is told)
        self,
        position,
        turns_left,
        neighbours=(),
        square_dug=False,
        on_cave=False,
        game_turn=1,
    ):
        """Ask the brain for this turn's decision, checking it's a real tool call."""
        view = TurnView(
            self._name,
            self._prompt,
            position,
            turns_left,
            self._earlier,
            neighbours,
            square_dug,
            on_cave,
            square_name(position, self._grid_size),
            self._turns_each,
            game_turn,
            edges_of(position, self._grid_size),
        )
        decision = self._brain.decide(view)
        if decision.action is not None and not is_action(decision.action):
            raise BadToolCall(f"{json.dumps(decision.action)} is not a tool call")
        self._pending = (position, decision, neighbours, square_dug, on_cave)
        return decision

    def remember(self, result, read_lines=()):
        """Tell the pirate what its last action did, and any lines its read found."""
        position, decision, neighbours, square_dug, on_cave = self._pending
        earlier = EarlierTurn(
            position,
            decision.action,
            result,
            decision.thinking,
            list(read_lines),
            neighbours,
            square_dug,
            on_cave,
            square_name(position, self._grid_size),
        )
        self._earlier = (*self._earlier, earlier)
