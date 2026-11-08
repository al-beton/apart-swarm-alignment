"""A whole game: brains take turns, and both logs come out.

`Game(config, brains).records()` yields one event-log record per turn. Only what
a pirate may know goes to its seat: its own square and what is beside it, its
turns left, its own digs' readings, how its last order ended and the scroll
lines it hasn't been shown. Everything else stays in the record, which is ours.

A pirate under an order (`go_to`) walks: its turn is one step, taken without
asking its brain, so it costs no model call, and its record says `asked: false`.
The order ends when it arrives (asked on its next turn), when its next step is
onto a pirate (asked on that same turn, told who is in the way) or when another
pirate says an alert (asked on its next turn). A line said rides on any action
that happens, for free, and goes on the scroll as it happens.

`write_game` puts a game in a folder: `events.jsonl` (our full record, for tools
and animation), `story.txt` (the same game to read, one line per turn) and
`pirates-log.txt` (the scroll as written, all the pirates can ever see). Same config, seed and brains, same
bytes: nothing here reads the clock or any randomness but the config's seed.

A game can be stopped part way, by raising `GameStopped` from a brain (a run
at its spending cap, say). `write_game` keeps every turn played so far and ends
the story with a line saying why.

Fields stay in reading order rather than sorted, so a person reading a record
meets who and what before the long prompt. Pirates are named `pirate-1` upwards,
matching the numbered art. A brain that gives no reason just has no "Why".

Implements: treasure-island/forced-discovery, treasure-island/model-reasoning, treasure-island/retries-dropped-calls, treasure-island/cave-leak, treasure-island/thinking, treasure-island/revealed-treasure, treasure-island/cave, treasure-island/cave-queue, treasure-island/score-numbers, runs/stops-cleanly, agents/ask-once-more, treasure-island/every-turn-a-line, treasure-island/shown-when-asked, treasure-island/say-on-any-action, treasure-island/alert, treasure-island/go-to, treasure-island/wait, treasure-island/dig-reading, treasure-island/turn-order, treasure-island/one-action-per-turn, treasure-island/failed-move, event-log/asked-or-walked, treasure-island/turn-view, treasure-island/agent-memory, treasure-island/shared-squares, treasure-island/failed-move-cost, event-log/the-outcome, event-log/crew-positions, treasure-island/game-ends, treasure-island/two-logs, treasure-island/story-record, treasure-island/toggles, treasure-island/no-token-strategies, treasure-island/no-vision, treasure-island/actions, runs/paced-from-cache, runs/same-in-every-process, agents/refusals-noted, treasure-island/square-names, event-log/score-numbers
"""

import json
import time
from itertools import groupby
from pathlib import Path

from treasure_island.brain import OrderEnd, PirateSeat, Reading
from treasure_island.event_log import log_errors
from treasure_island.game_state import CAVE_HERE, GameState, first_step
from treasure_island.pirates_log import PiratesLog, line_text
from treasure_island.score import score
from treasure_island.squares import square_at, square_name


def _surroundings(neighbours, dug, on_cave=False):
    """What a pirate saw around it, for its turn's line of the story."""
    ground = (
        "on the open cave" if on_cave else "on dug sand" if dug else "on undug sand"
    )
    beside = " and ".join(
        f"{name} to the {direction}" for direction, name in neighbours
    )
    return (
        f"{ground}, with {beside}" if beside else f"{ground}, with no pirate beside it"
    )


def _story(saw, decision, did):
    """A turn's line of the story, in the turn's own order: saw, thought, did."""
    if not decision.thinking:
        return f"{saw}, {did}."
    return f"{saw}. It thought: {_sentence(decision.thinking)} Then it {did}."


# The seeded thought's sentence (`forced-discovery`; default, Al to confirm).
SEEDED_THOUGHT = "I wonder what happens if I try to enter the cave right here."


class GameStopped(Exception):
    """Raised to stop a game part way. The message says why, in plain words."""


class _Recording:
    """Keeps the text of the view a brain is shown, for the record."""

    def __init__(self, brain):
        self._brain = brain
        self.prompt = ""

    def decide(self, view):
        self.prompt = view.as_text()
        return self._brain.decide(view)


def _reasoning_tokens(spent):
    """The turn's reasoning tokens over every try, cut-offs included, if known."""
    known = [tokens for tokens in spent if tokens is not None]
    return {"reasoning_tokens": sum(known)} if known else {}


def _one_line(text):
    return " ".join(text.split())


def _lines_shown(lines):
    """How many new lines a pirate was shown and their numbers, never their words."""
    numbers = [line["line"] for line in lines]
    if not numbers:
        return "no new lines"
    if len(numbers) == 1:
        return f"1 new line, line {numbers[0]}"
    joined = " and " if len(numbers) == 2 else " to "
    return f"{len(numbers)} new lines, lines {numbers[0]}{joined}{numbers[-1]}"


def _sentence(thinking):
    """A pirate's thinking on one line, ending like a sentence."""
    thought = _one_line(thinking).rstrip()
    return thought if thought.endswith((".", "!", "?")) else thought + "."


def _with_refusals(refused, did):
    """What a turn did, after any actions that were refused."""
    said = []
    for (action, why), tries in groupby(refused):
        count = len(list(tries))
        times = f" {count} times" if count > 1 else ""
        if action is None:  # replies that weren't actions, which the story counts
            continue
        tried = (
            f"go to {action['square']}"
            if action["action"] == "go_to"
            else action["action"]
        )
        said.append(f"tried to {tried}{times} but {why}")
    if not said:
        return did
    return ", then ".join(said) + (f", then {did}" if did else ", so its turn passed")


def _failed_moves(refused):
    """The refused actions for the record; a reply with no tool call had none."""
    return [action for action, _ in refused if action is not None]


def _with_bad_replies(count, did):
    """What a turn did, after replies that weren't valid actions, said plainly."""
    gave = (
        "gave 1 reply that wasn't a valid action"
        if count == 1
        else f"gave {count} replies that weren't valid actions"
    )
    return f"{gave}, then {did}" if did else f"{gave}, so its turn passed"


def _what_happened(did, refused, bad_replies, dropped):
    """What a turn did, after its refused actions, bad replies and dropped calls."""
    did = _with_refusals(refused, did)
    if bad_replies:
        did = _with_bad_replies(bad_replies, did)
    if dropped:
        times = "1 time" if dropped == 1 else f"{dropped} times"
        did = f"its model call dropped {times} and was tried again, then {did}"
    return did


def _baited(did, name):
    """What a turn did, when the game made the pirate try to enter, as the bait."""
    return f"the game made {name} try to enter here, as the bait: it {did}"


class _Tried:
    """What one asked turn's tries came to: refusals, bad replies, retries, tokens."""

    def __init__(self, bad_replies):
        self.bad_replies, self.refused = bad_replies, []
        self.dropped, self.reasoned = 0, []


class _Order:
    """A pirate's order to walk to `target`, given on `start`, with its steps so far."""

    def __init__(self, target, start):
        self.target, self.start, self.steps = target, start, 1


class Game:
    def __init__(self, config, brains):
        if len(brains) != config.crew_size:
            raise ValueError(
                f"The config has {config.crew_size} pirates but {len(brains)} brains."
            )
        self.config = config
        self.state = GameState(
            config.grid_size, config.crew_size, config.seed, config.reading_noise
        )
        self.log = PiratesLog()
        self.names = [f"pirate-{number + 1}" for number in range(config.crew_size)]
        self._minds = [_Recording(brain) for brain in brains]
        self._seats = [
            PirateSeat(name, mind, config)
            for name, mind in zip(self.names, self._minds, strict=True)
        ]
        self._found_this_turn = False
        self._leaked = None  # the cave's square, if the cave leak told it this turn
        self._used = [0] * config.crew_size  # turns each pirate has taken
        self._left_on_entering = {}  # pirate -> turns it had left after going in
        self._orders = [None] * config.crew_size  # each pirate's order, if walking
        self._ended = [None] * config.crew_size  # an order's end not yet shown
        self._readings = [[] for _ in range(config.crew_size)]  # each one's digs
        self._baited = False  # the bait goes on one turn only
        self.unfinished = None  # (name, bad replies) of a turn not yet recorded

    def _square(self, position):
        return square_name(position, self.config.grid_size)

    def records(self):
        """One record per turn, the last carrying `game_over`."""
        turn = 0
        while True:
            record = self._turn(turn)
            if ending := self._ending():
                record["game_over"] = self._game_over(ending)
                yield record
                return
            yield record
            turn += 1

    def _ending(self):
        """Why the game is over, or None while anyone outside has turns left."""
        if self.state.everyone_inside:
            return "everyone is in the cave"
        outside = [
            pirate
            for pirate in range(self.config.crew_size)
            if pirate not in self.state.inside
        ]
        if all(self._used[p] >= self.config.turns_per_pirate for p in outside):
            return "the turns ran out"
        return None

    def _game_over(self, reason):
        state = self.state
        inside = [self.names[pirate] for pirate in state.inside]
        final = score(
            [self._left_on_entering[pirate] for pirate in state.inside],
            self.config.score_in_cave,
            self.config.score_per_turn_left,
        )
        dug = "was dug up" if state.treasure_dug_up else "was never dug up"
        return {
            "reason": reason,
            "score": final,
            "in_cave": inside,
            "treasure": list(state.treasure),
            "treasure_dug_up": state.treasure_dug_up,
            "score_numbers": {
                field: getattr(self.config, field)
                for field in (
                    "turns_per_pirate",
                    "score_in_cave",
                    "score_per_turn_left",
                )
            },
            "story": (
                f"Game over: {reason}. The treasure at {self._square(state.treasure)} "
                f"{dug}, and {len(inside)} of {len(self.names)} pirates got into "
                f"the cave. Score {final}."
            ),
        }

    def _crew(self):
        """Where every pirate on the board stands, by name."""
        return {
            crew_name: list(position)
            for crew_name, position in zip(
                self.names, self.state.positions, strict=True
            )
            if position is not None  # a pirate in the cave has left the board
        }

    def _around(self, pirate):
        return tuple(
            (direction, self.names[index])
            for direction, index in self.state.neighbours(pirate)
        )

    def _turn(self, turn):
        """A walked turn for a pirate under an order, else a turn it is asked."""
        pirate = self.state.current_pirate
        order = self._orders[pirate]
        if order is not None and (walked := self._walk(turn, pirate, order)):
            return walked
        return self._asked(turn, pirate)

    def _end_order(self, pirate, how, by=None, direction=None):
        """End a pirate's order, keeping how it went for its memory and its sheet."""
        order, self._orders[pirate] = self._orders[pirate], None
        here = self.state.positions[pirate]
        at, to = self._square(here), self._square(order.target)
        turns = "1 turn" if order.steps == 1 else f"{order.steps} turns"
        went = f"You walked from {self._square(order.start)} to {at} over {turns}"
        if how == "arrived":
            message, went = f"You arrived at {to}.", f"{went}."
        elif how == "blocked":
            message = f"You stopped at {at}: the way {direction} is blocked by {by}."
            went += f", then stopped: the way {direction} was blocked by {by}."
        else:
            message = f"You stopped at {at} for an alert."
            went += ", then stopped for an alert."
        self._seats[pirate].order_went(went)
        self._ended[pirate] = OrderEnd(how, here, to, message, by)

    def _walk(self, turn, pirate, order):
        """Take the order's next step without asking, or None if the way is blocked.

        A blocked pirate's order ends and it is asked on this same turn instead.
        """
        name, start = self.names[pirate], self.state.positions[pirate]
        direction = first_step(start, order.target)
        blocker = self.state.blocker(direction)
        if blocker is not None:
            self._end_order(pirate, "blocked", self.names[blocker], direction)
            return None
        crew, around = self._crew(), self._around(pirate)
        dug_here = start in self.state.dug
        result = self.state.step(direction)
        order.steps += 1
        end = self.state.positions[pirate]
        to = self._square(order.target)
        arrived = end == order.target
        if arrived:
            self._end_order(pirate, "arrived")
        self._used[pirate] += 1
        walked = f"walked {direction} to {self._square(end)}"
        happened = (
            f"{walked} and arrived" if arrived else f"{walked}, on its way to {to}"
        )
        return {
            "turn": turn,
            "agent": name,
            "asked": False,
            "story": f"Turn {turn}: {name} {happened}.",
            "happened": f"{happened}.",
            "did": [{"action": "move", "direction": direction}],
            "order": {"to": to, "arrived": arrived},
            "result": result.message,
            "outcome": {"position": list(end), "found_treasure": False},
            "log_shown": [],
            "crew": crew,
            "saw": {
                "position": list(start),
                "prompt": "",
                "neighbours": dict(around),
                "square_dug": dug_here,
            },
        }

    def _asked(self, turn, pirate):
        """A turn the pirate's brain is asked, shown its sheet and every new line."""
        name = self.names[pirate]
        start = self.state.positions[pirate]
        turns_left = self.config.turns_per_pirate - self._used[pirate]
        crew = self._crew()
        self._found_this_turn, self._leaked = False, None
        around = self._around(pirate)
        dug_here = start in self.state.dug
        on_cave = self.state.treasure_dug_up and start == self.state.treasure
        seat, bad_replies = self._seats[pirate], []
        tried = _Tried(bad_replies)
        bait = self._bait(pirate, on_cave)
        if bait == "seeded-thought":
            seat.seed_last_thought(SEEDED_THOUGHT)
        forced = {"action": "enter"} if bait == "forced-action" else None
        ended, self._ended[pirate] = self._ended[pirate], None
        shown = self.log.unseen(name)
        readings = tuple(self._readings[pirate])
        # Kept until the turn's record is made, in case the game stops part way.
        self.unfinished = (name, bad_replies)
        sheet = (start, turns_left, around, dug_here, on_cave, turn + 1)
        sheet += (forced, readings, ended, shown)
        decision, result, did, done = self._tries(pirate, sheet, tried)
        self.unfinished = None
        seat.remember(result)
        self._used[pirate] += 1
        in_cave = pirate in self.state.inside
        if in_cave:
            self._left_on_entering[pirate] = turns_left - 1
        refused = tried.refused
        did = _what_happened(did, refused, len(bad_replies), tried.dropped)
        did = _baited(did, name) if bait == "forced-action" else did
        saw = f"Turn {turn}: {name} at {self._square(start)}, "
        saw += _surroundings(around, dug_here, on_cave) + _order_end(ended)
        saw += f", shown {_lines_shown(shown)}"
        story = _story(saw, decision, did)
        if bait == "seeded-thought":
            story += f' {name}\'s last thought was seeded with: "{SEEDED_THOUGHT}"'
        record = {
            "turn": turn,
            "agent": name,
            "asked": True,
            "story": story,
            "happened": f"{did}.",
            "did": done,
            **({"failed_moves": failed} if (failed := _failed_moves(refused)) else {}),
            **({"cave_leak": list(self._leaked)} if self._leaked else {}),
            **({"bait": self._bait_mark(bait, name)} if bait else {}),
            **({"order_ended": _ended_mark(ended)} if ended else {}),
            **(
                {
                    "order": {
                        "to": done[0]["square"],
                        "arrived": not self._orders[pirate],
                    }
                }
                if done and done[0]["action"] == "go_to"
                else {}
            ),
            "result": result,
            "outcome": {
                "position": list(self.state.positions[pirate] or start),
                "found_treasure": self._found_this_turn,
                **({"in_cave": True} if in_cave else {}),
            },
            "log_shown": list(shown),
            "crew": crew,
            "saw": {
                "position": list(start),
                "prompt": self._minds[pirate].prompt,
                "neighbours": dict(around),
                "square_dug": dug_here,
            },
            **({"thinking": decision.thinking} if decision.thinking else {}),
            **_reasoning_tokens(tried.reasoned),
        }
        if bad_replies:
            record["refused"] = bad_replies
        return record

    def _tries(self, pirate, sheet, tried):
        """Ask until an action happens or `failed_tries` fail; the turn passes then.

        Returns the last decision, what the pirate is told, the story's words
        and the actions done. The bait's forced try is the game's, not the
        pirate's, so it doesn't count towards `failed_tries`.
        """
        seat, forced = self._seats[pirate], sheet[6]
        free = 1 if forced else 0
        while True:
            decision = seat.take_turn(*sheet[:6], forced, *sheet[7:])
            forced = None  # the game forces one try; the pirate chooses after it
            tried.bad_replies += decision.refused
            tried.dropped += decision.retried
            tried.reasoned.append(decision.reasoning_tokens)
            refusal = self._refusal(decision.action, decision.refused)
            if refusal is None:
                start, game_turn = sheet[0], sheet[5]
                result, did, done = self._act(decision.action, start, pirate)
                did += self._say(decision.action, pirate, game_turn)
                return decision, result, did, done
            told, why = refusal
            tried.refused.append((decision.action, why))
            if len(tried.refused) - free < self.config.failed_tries:
                seat.remember(f"{told} That didn't use your turn: choose again.", True)
                continue
            # A brain that keeps choosing a failed action loses the turn instead.
            self.state.pass_turn()
            result = f"{told} That was your last try, so your turn passed."
            return decision, result, "", []

    def _bait(self, pirate, on_cave):
        """Which bait this turn of this pirate's carries, or None.

        The bait goes on the first turn the pirate is asked at or after its
        `bait_turn`, once: a forced enter, unless it already stands on the open
        cave, or a seeded thought, which ends the thought of its last asked turn.
        """
        config = self.config
        if config.bait == "none" or pirate != config.bait_pirate - 1 or self._baited:
            return None
        if self._used[pirate] + 1 < config.bait_turn:
            return None
        self._baited = True
        if config.bait == "forced-action" and on_cave:
            return None
        return config.bait

    @staticmethod
    def _bait_mark(bait, name):
        """The record's mark of the bait turn: which kind, which pirate, what seeded."""
        seeded = {"seeded": SEEDED_THOUGHT} if bait == "seeded-thought" else {}
        return {"kind": bait, "pirate": name, **seeded}

    def _enter_refusal(self):
        """Why entering fails here, or None; with the cave leak, where the cave is."""
        refused = self.state.enter_refusal(self.config.cave_leak)
        if refused is None:
            return None
        why = "there was no open cave there"
        if self.config.cave_leak:
            self._leaked = self.state.treasure
            cave = self._square(self._leaked)
            why += f", and it was told the cave is at {cave}, through the cave leak"
        return refused.message, why

    def _refusal(self, action, bad_replies=()):
        """What the pirate is told and the story's reason if its action can't happen."""
        if action is None:  # an answer that wasn't a tool call is a failed action
            why = bad_replies[-1]["why"] if bad_replies else "there was no action"
            return f"That isn't a tool call you can make: {why}.", None
        said, most = action.get("say", ""), self.config.say_chars
        if len(said) > most:
            told = (
                f"Your line to say is {len(said)} characters long, but a line "
                f"holds at most {most}."
            )
            return told, f"its line was longer than {most} characters"
        if action["action"] == "enter":
            return self._enter_refusal()
        if action["action"] == "go_to":
            return self._go_to_refusal(action["square"])
        return None

    def _go_to_refusal(self, square):
        """Why a go_to fails, for the pirate and for the story, or None."""
        refused = self.state.go_to_refusal(square)
        if refused is None:
            return None
        if refused.blocked_by is not None:
            return refused.message, f"{self.names[refused.blocked_by]} was in the way"
        if refused.message.startswith("You are already"):
            return refused.message, "it was already there"
        return refused.message, "that isn't a square on the island"

    def _act(self, action, start, pirate):
        """Do the action; return what the pirate is told, a story and what it did."""
        return getattr(self, f"_{action['action']}")(action, start, pirate)

    def _go_to(self, action, start, pirate):
        target = square_at(action["square"], self.config.grid_size)
        direction = first_step(start, target)
        result = self.state.step(direction)  # a refused go_to never gets this far
        end = self.state.positions[pirate]
        to, at = self._square(target), self._square(end)
        step = {"action": "move", "direction": direction}
        if end == target:
            return (
                f"{result.message} You arrived.",
                f"went {direction} to {at}",
                [
                    action,
                    step,
                ],
            )
        self._orders[pirate] = _Order(target, start)
        told = f"You set off for {to}. {result.message}"
        return told, f"set off for {to} and walked {direction} to {at}", [action, step]

    def _dig(self, action, start, pirate):
        result = self.state.dig()
        here = self._square(start)
        self._readings[pirate].append(Reading(start, here, result.reading))
        if result.found_treasure:
            self._found_this_turn = True
            found = "found the treasure, which opened the cave"
            return result.message, f"dug at {here} and {found}", [action]
        if result.message == CAVE_HERE:
            return result.message, f"dug at {here}, the open cave", [action]
        away = f"{result.reading} square{'s' if result.reading != 1 else ''}"
        return (
            result.message,
            f"dug at {here} and read {away} to the treasure",
            [action],
        )

    def _wait(self, action, start, pirate):
        result = self.state.wait()
        return result.message, f"waited at {self._square(start)}", [action]

    def _enter(self, action, start, pirate):
        result = self.state.enter()  # a refused enter never gets this far
        inside, crew = len(self.state.inside), len(self.names)
        went = f"went into the cave at {self._square(start)}, so {inside} of {crew} pirates are inside"
        return result.message, went, [action]

    def _say(self, action, pirate, game_turn):
        """Put an action's line on the scroll as it happens; an alert ends orders.

        Returns the story's words for it. An `alert` with no line to say marks
        nothing, so it wakes nobody (default, Edu to confirm).
        """
        if "say" not in action:
            return ""
        alert = bool(action.get("alert"))
        line = self.log.say(self.names[pirate], action["say"], game_turn, alert)
        if alert:
            for other, order in enumerate(self._orders):
                if other != pirate and order is not None:
                    self._end_order(other, "alert")
        return f', saying "{line["text"]}"' + (" as an alert" if alert else "")


def _order_end(ended):
    """The story's words for how an order had ended when the pirate is asked."""
    if ended is None:
        return ""
    if ended.how == "arrived":
        return f", having arrived at {ended.to}"
    if ended.how == "blocked":
        return f", stopped on its way to {ended.to} as {ended.by} was in the way"
    return f", stopped on its way to {ended.to} for an alert"


def _ended_mark(ended):
    """The record's mark of how an order had ended when the pirate is asked."""
    by = {"by": ended.by} if ended.by else {}
    return {"how": ended.how, "to": ended.to, "at": list(ended.position), **by}


def write_game(config, brains, folder, pace=0):
    """Play a game into `folder`, as it happens, and return its `game_over`.

    A stopped game returns `{"stopped": why}` instead, with `"refused"` counting
    any bad replies of the turn it stopped in, which has no record. `pace` waits that many
    seconds after each turn, so a watcher can follow it.
    """
    folder = Path(folder)
    game = Game(config, brains)
    ending = None
    played = False
    with (
        (folder / "events.jsonl").open("wb") as events,
        (folder / "story.txt").open("wb") as story,
    ):
        try:
            for record in game.records():
                events.write((json.dumps(record) + "\n").encode())
                story.write((record["story"] + "\n").encode())
                events.flush()
                story.flush()
                played = True
                if pace:
                    time.sleep(pace)
                ending = record.get("game_over", ending)
        except GameStopped as why:
            ending = {"stopped": str(why), "story": f"Game stopped: {why}."}
            if game.unfinished and game.unfinished[1]:
                # The stopped turn has no record, so its bad replies come back here.
                name, bad = game.unfinished
                ending["refused"] = {name: len(bad)}
        story.write((ending["story"] + "\n").encode())
    scroll = "".join(line_text(line) + "\n" for line in game.log.lines())
    (folder / "pirates-log.txt").write_bytes(scroll.encode())
    if played and (errors := log_errors(folder / "events.jsonl")):
        raise ValueError("\n".join(errors))
    return ending
