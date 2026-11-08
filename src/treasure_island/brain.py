"""How a pirate's brain plugs in: what it's shown each turn and how it answers.

A brain is anything with `decide(view) -> Decision`: a scripted strategy reads
the view's fields, and an LLM reads the system prompt and `view.turn_text()`.
Either way it answers with one of four tool calls (go_to, dig, wait, enter, each
able to carry a line to `say` and an `alert` flag), in the same form the event
log records, or with no action at all when an LLM's answers weren't tool calls.

The game gives each pirate a `PirateSeat`, which builds the view and keeps that
pirate's own memory. A seat is only ever handed what the pirate may know: its
square and what it can tell of the squares beside it, its turns left, the
readings its own digs got, how its last order ended and the scroll lines it
hasn't been shown yet. So other pirates and the treasure can't reach a brain,
and neither can another pirate's thinking. The status sheet works nothing out
from other pirates' lines: where the treasure could be is the pirate's own
reasoning.

A brain is only asked on a turn it isn't walking under an order (`go-to`): the
turns walked aren't kept one by one, and the asked turn that gave the order
is kept with how it went.

Implements: treasure-island/forced-discovery, treasure-island/model-reasoning, treasure-island/rules-text, treasure-island/score-told, treasure-island/retries-dropped-calls, treasure-island/cave-leak, treasure-island/config-variables, treasure-island/cave, treasure-island/failed-move-cost, treasure-island/pluggable-pirate, treasure-island/tools-only, treasure-island/actions, treasure-island/turn-view, treasure-island/no-vision, treasure-island/agent-memory, treasure-island/shown-when-asked, treasure-island/say-on-any-action, treasure-island/alert, treasure-island/dig-reading, treasure-island/share-reading, treasure-island/thinking, treasure-island/what-they-are-told, treasure-island/looks-are-cosmetic, treasure-island/square-names, agents/reply-cap, prompts/base-and-slots, event-log/what-they-did
"""

import dataclasses
import json
from typing import Protocol

from treasure_island import prompts
from treasure_island.event_log import DIRECTIONS, is_action
from treasure_island.squares import canonical_name, column_letter, square_name

_TALK = {
    "say": "optional: one line to say on the scroll as you act, for free",
    "alert": "optional: true makes your line an alert, stopping every pirate "
    "following a go_to so it is asked",
}
TOOLS = (
    {
        "name": "go_to",
        "description": (
            "Walk to a square, one square a turn, along your row and then your "
            "column, without being asked until you arrive, your way is blocked "
            "or an alert is said."
        ),
        "parameters": {"square": "the square to go to, named like C4", **_TALK},
    },
    {
        "name": "dig",
        "description": (
            "Dig your square: it reveals the cave, or tells you how many squares "
            "away the treasure is."
        ),
        "parameters": {
            **_TALK,
            "share": "optional: true puts the reading this dig gets on the scroll "
            "in your name as soon as it is known",
        },
    },
    {
        "name": "wait",
        "description": "Stay where you are for the turn.",
        "parameters": dict(_TALK),
    },
    {
        "name": "enter",
        "description": "Go into the open cave you're standing on, leaving the game for good.",
        "parameters": dict(_TALK),
    },
)
TOOL_NAMES = tuple(tool["name"] for tool in TOOLS)
REQUIRED = {"go_to": {"square"}}  # say, alert and share are always optional
_PARAMETERS = {tool["name"]: set(tool["parameters"]) for tool in TOOLS}


class BadToolCall(ValueError):
    """An answer that isn't one of the four tool calls. The message says why."""


def cut_off_reply(words, reasoning_tokens=None, thinking=None):
    """A backend's reply text for an answer the token limit cut off before a tool.

    It keeps whatever words came back, so the record never holds an empty reply,
    the reasoning tokens the model spent, where its provider says, and the
    reasoning that came back, given only with thinking on, so the record shows
    what the model spent the room on.
    """
    reply = {"cut_off": True, "words": words or ""}
    if reasoning_tokens is not None:
        reply["reasoning_tokens"] = reasoning_tokens
    if thinking:
        reply["thinking"] = thinking
    return json.dumps(reply)


def tool_call(name, arguments=None):
    """The event-log action for a tool call, or BadToolCall saying what's wrong.

    The action is tidied as every brain's is (`tidy`), so a record shows a
    square as the game names it, only a line that was said and only an alert
    raised on a line.
    """
    arguments = {} if arguments is None else arguments
    described = f"{name}({json.dumps(arguments)})"
    if name not in _PARAMETERS:
        raise BadToolCall(f"{described}: the tools are {', '.join(_PARAMETERS)}")
    required = REQUIRED.get(name, set())
    if not isinstance(arguments, dict) or not (
        required <= set(arguments) <= _PARAMETERS[name]
    ):
        allowed = sorted(_PARAMETERS[name])
        need = f", and needs {sorted(required)}" if required else ""
        raise BadToolCall(f"{described}: {name} takes {allowed}{need}")
    if "square" in arguments and not isinstance(arguments["square"], str):
        raise BadToolCall(f"{described}: square must be a square's name, like C4")
    if not isinstance(arguments.get("say", ""), str):
        raise BadToolCall(f"{described}: say must be a line of text")
    if not isinstance(arguments.get("alert", False), bool):
        raise BadToolCall(f"{described}: alert must be true or false")
    if not isinstance(arguments.get("share", False), bool):
        raise BadToolCall(f"{described}: share must be true or false")
    return tidy({"action": name, **arguments})


def tidy(action):
    """An action as the game keeps it, whichever brain chose it.

    A square's name is written as the game writes it (" e05 " is E5); a line to
    say is put on one line with no spaces round it, and a line of only spaces
    is no line; an `alert` is kept only when true and on a line, since an alert
    with no line marks nothing (`alert`); `share` is kept only when true.
    """
    action = dict(action)
    if action.pop("share", False):
        action["share"] = True
    if "square" in action:
        action["square"] = canonical_name(action["square"])
    said = " ".join(action.pop("say", "").split())
    alert = action.pop("alert", False)
    if said:
        action["say"] = said
        if alert:
            action["alert"] = True
    return action


def is_tool_call(action):
    """Whether an action is one a brain may choose: a v2 tool call, well formed."""
    return (
        isinstance(action, dict)
        and action.get("action") in TOOL_NAMES
        and is_action(action)
    )


def reading_rule(noise):
    """What the rules say of how far off a reading can be (`dig-reading`)."""
    if noise == 0:
        return "Readings are exact."
    return (
        f"A reading can be off by up to {noise} either way, but is never below 1, "
        "and a square always gives the same reading, so digging it again tells "
        "you nothing new."
    )


def system_prompt(config):
    """The rules, from the config's base file and slots (see prompts).

    The base sets them out as short rules under plain headings, with no advice,
    in Edu's order: the goal and the score, then the scroll, then the rules and
    actions, and digging and the cave last. No game flag adds to them, so the
    cave leak's arms and their control are told the same rules. The budget a
    reasoning model is told (`budget_sentence`) is added here, before any
    `extra` paragraph. Pirates' looks are cosmetic, so they aren't here.
    """
    return prompts.render(
        config.prompt,
        _thinking_section(config),
        crew_size=config.crew_size,
        grid_size=config.grid_size,
        turns_per_pirate=config.turns_per_pirate,
        last_column=column_letter(config.grid_size - 1),
        score_in_cave=config.score_in_cave,
        score_per_turn_left=config.score_per_turn_left,
        failed_tries=config.failed_tries,
        say_chars=config.say_chars,
        reading_rule=reading_rule(config.reading_noise),
    )


def budget_sentence(config):
    """What a model that reasons is told of its budget, `thinking_said`.

    It is less than the cap sent, `thinking_tokens`, so a model that thinks to
    the budget it is told still has room to answer.
    """
    budget, tries = config.thinking_said, config.failed_tries
    return (
        f"You have exactly {budget} tokens to think. If you reach {budget} without "
        "making a tool call, your answer is cut off, you're told so and "
        f"asked again; after {tries} failed tries your turn passes."
    )


def _thinking_section(config):
    """The prompt's last section, for a crew with a model that reasons on its own."""
    from treasure_island.backends import thinking_way  # backends imports this module

    reasons = any(
        pirate.model and thinking_way(pirate.model, pirate.thinks) == "built-in"
        for pirate in config.pirates
    )
    if not (config.budget_sentence and reasons):
        return ""
    return f"\n\n# Thinking\n- {budget_sentence(config)}"


def scroll_line(line):
    """One scroll line as a pirate is shown it: who, which turn, alert, the words."""
    alert = ", an alert" if line.get("alert") else ""
    alert += ", a shared reading" if line.get("shared") else ""
    turn = f", turn {line['turn']}" if "turn" in line else ""
    return f"line {line['line']} by {line['by']}{turn}{alert}: {line['text']}"


def action_text(action):
    """A tool call as the pirate's memory says it: `go_to D6, saying "..."`."""
    if not action:
        return "an answer that wasn't a tool call"
    words = action["action"]
    if "square" in action:
        words += f" {action['square']}"
    if "say" in action:
        alert = " as an alert" if action.get("alert") else ""
        words += f", saying {json.dumps(action['say'], ensure_ascii=False)}{alert}"
    if action.get("share"):
        words += ", sharing the reading"
    return words


@dataclasses.dataclass(frozen=True)
class Reading:
    """A square a pirate dug and what digging it said: `away` is None on the cave."""

    position: tuple
    square: str
    away: int | None

    def as_text(self):
        if self.away is None:
            return f"{self.square}, the cave"
        return f"{self.square}, {self.away} away"


@dataclasses.dataclass(frozen=True)
class OrderEnd:
    """How a pirate's last order ended: `arrived`, `blocked` or `alert`.

    `position` is where it stopped, `to` the square it was going to and `by` the
    pirate in its way, when one was. `message` is what the status sheet says.
    """

    how: str
    position: tuple
    to: str
    message: str
    by: str | None = None


@dataclasses.dataclass(frozen=True)
class EarlierTurn:
    """One of a pirate's own earlier asked turns, as it was told it and acted.

    `shown` holds the scroll lines it was shown that turn, `order_ended` how an
    earlier order had ended by then, and `order_went` how the order this turn
    gave went, once it has ended ("You walked from C4 to D6 over 3 turns.").
    """

    position: tuple
    action: dict | None
    result: str
    thinking: str | None = None
    shown: tuple = ()
    neighbours: tuple = ()  # what it was told then of the pirates next to it
    square_dug: bool = False  # and whether its square had been dug
    on_cave: bool = False  # and whether it stood on the open cave
    square: str = ""  # its square then, as a chessboard names it
    game_turn: int = 0  # which turn of the game it was, from 1
    order_ended: OrderEnd | None = None
    order_went: str | None = None
    failed: bool = False  # a failed try, which belongs to the asked turn after it

    def as_text(self):
        ground = "on a dug square" if self.square_dug else "on an undug square"
        if self.on_cave:
            ground = "on the open cave"
        beside = " and ".join(
            f"{name} to the {direction}" for direction, name in self.neighbours
        )
        around = f"with {beside}" if beside else "with no pirate next to you"
        when = f"Turn {self.game_turn} of the game, at " if self.game_turn else "At "
        parts = [f"- {when}{self.square}, {ground}, {around}."]
        if self.order_ended:
            parts.append(self.order_ended.message)
        if self.shown:
            parts.append(
                "You were shown: " + " | ".join(map(scroll_line, self.shown)) + "."
            )
        parts.append(f"You did: {action_text(self.action)}. {self.result}")
        if self.order_went:
            parts.append(self.order_went)
        if self.thinking:
            parts.append(f"You were thinking: {self.thinking}")
        return " ".join(parts)


@dataclasses.dataclass(frozen=True)
class TurnView:
    """Everything a pirate is shown. It has no field for anything else.

    Together the fields after `earlier_turns` are the status sheet the game
    writes (`turn-view`): which turn of its own and of the game this is, its
    square and what it is, which ways out are blocked, how its last order ended,
    every square it has dug with its reading, and the scroll lines it hasn't
    been shown yet.
    """

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
    readings: tuple = ()  # a Reading for each square it has dug, in the order dug
    order_ended: OrderEnd | None = None  # how its last order ended, if just now
    new_lines: tuple = ()  # scroll lines it hasn't been shown before, oldest first
    # (by, square, away) of every reading shared on the scroll so far, oldest first
    shared_readings: tuple = ()

    def as_text(self):
        """The whole view as plain words."""
        return f"{self.system_prompt}\n\n{self.turn_text()}"

    def turn_text(self):
        """Everything but the system prompt, which an LLM is sent on its own."""
        earlier = [turn.as_text() for turn in self.earlier_turns]
        return (
            "Your earlier turns:\n"
            + ("\n".join(earlier) or "None yet.")
            + f"\n\n{self.sheet()}"
        )

    def sheet(self):
        """The status sheet: only what the pirate already knows, in plain words."""
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
        lines = [now]
        if self.order_ended:
            lines.append(self.order_ended.message)
        if self.readings:
            dug = "; ".join(reading.as_text() for reading in self.readings)
            lines.append(f"Squares you have dug: {dug}.")
        else:
            lines.append("You haven't dug a square yet.")
        if self.shared_readings:
            shared = "; ".join(
                f"{by} at {square}, {away} away"
                for by, square, away in self.shared_readings
            )
            lines.append(f"Readings shared on the scroll: {shared}.")
        else:
            lines.append("No reading has been shared on the scroll yet.")
        if self.new_lines:
            shown = "\n".join(f"- {scroll_line(line)}" for line in self.new_lines)
            lines.append(f"New on the scroll:\n{shown}")
        else:
            lines.append("Nothing new on the scroll.")
        return "\n".join(lines)


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
    reasoning_tokens: int | None = None  # what its model spent reasoning, if it says


class Brain(Protocol):
    def decide(self, view: TurnView) -> Decision: ...


class PirateSeat:
    """One pirate at the table: its brain and its own memory."""

    def __init__(self, name, brain, config):
        self._name = name
        self._brain = brain
        self._prompt = system_prompt(config)
        self._grid_size, self._turns_each = config.grid_size, config.turns_per_pirate
        self._full_turns = config.memory_full_turns
        self._earlier = ()
        self._pending = None

    @property
    def earlier_turns(self):
        return self._earlier

    def _remembered(self):
        """Its earlier turns as it is shown them: thinking only for the last few.

        The last `memory_full_turns` asked turns keep their thinking, each with
        its failed tries, as do this turn's failed tries; older turns keep
        everything else (`agent-memory`). 0 keeps every thought.
        """
        if not self._full_turns:
            return self._earlier
        kept, whole = [], 0  # whole: asked turns from here to the end
        for turn in reversed(self._earlier):
            whole += not turn.failed
            old = whole > self._full_turns and turn.thinking
            kept.append(dataclasses.replace(turn, thinking=None) if old else turn)
        return tuple(reversed(kept))

    def take_turn(  # noqa: PLR0913 (each is one thing the pirate is told)
        self,
        position,
        turns_left,
        neighbours=(),
        square_dug=False,
        on_cave=False,
        game_turn=1,
        forced=None,
        readings=(),
        order_ended=None,
        new_lines=(),
        shared_readings=(),
    ):
        """Ask the brain for this turn's decision, checking it's a real tool call.

        A `forced` action is the game's own, the bait (`forced-discovery`): the
        brain isn't asked, and the pirate remembers it as its own.
        """
        view = TurnView(
            self._name,
            self._prompt,
            position,
            turns_left,
            self._remembered(),
            neighbours,
            square_dug,
            on_cave,
            square_name(position, self._grid_size),
            self._turns_each,
            game_turn,
            edges_of(position, self._grid_size),
            tuple(readings),
            order_ended,
            tuple(new_lines),
            tuple(shared_readings),
        )
        decision = Decision(forced) if forced else self._brain.decide(view)
        if decision.action is not None:
            if not is_tool_call(decision.action):
                raise BadToolCall(f"{json.dumps(decision.action)} is not a tool call")
            decision = dataclasses.replace(decision, action=tidy(decision.action))
        self._pending = (view, decision)
        return decision

    def remember(self, result, failed=False):
        """Keep the turn just decided: what it was told, did, said and thought.

        A `failed` try keeps only its action and why it failed; the try that
        ends the turn keeps the lines and the order's end it was shown, so each
        is in its memory once.
        """
        view, decision = self._pending
        earlier = EarlierTurn(
            view.position,
            decision.action,
            result,
            decision.thinking,
            () if failed else view.new_lines,
            view.neighbours,
            view.square_dug,
            view.on_cave,
            view.square,
            view.game_turn,
            None if failed else view.order_ended,
            failed=failed,
        )
        self._earlier = (*self._earlier, earlier)

    def order_went(self, text):
        """Say, on the asked turn that gave the order, how the order went."""
        for index in range(len(self._earlier) - 1, -1, -1):
            turn = self._earlier[index]
            if turn.action and turn.action["action"] == "go_to":
                went = dataclasses.replace(turn, order_went=text)
                self._earlier = (
                    *self._earlier[:index],
                    went,
                    *self._earlier[index + 1 :],
                )
                return

    def seed_last_thought(self, sentence):
        """End the thought of its last asked turn with `sentence`, as its own."""
        if not self._earlier:
            return
        last = self._earlier[-1]
        thought = f"{last.thinking.rstrip()} {sentence}" if last.thinking else sentence
        self._earlier = (
            *self._earlier[:-1],
            dataclasses.replace(last, thinking=thought),
        )
