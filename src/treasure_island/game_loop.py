"""A whole game: brains take turns, and both logs come out.

`Game(config, brains).records()` yields one event-log record per turn. Only what
a pirate may know goes to its seat: its own position, its turns left and what
its reads found on the scroll. Everything else stays in the record, which is ours.

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

Implements: runs/stops-cleanly, agents/ask-once-more, treasure-island/every-turn-a-line, treasure-island/reading-costs, treasure-island/turn-view, treasure-island/agent-memory, treasure-island/shared-squares, treasure-island/failed-move-cost, event-log/the-outcome, event-log/crew-positions, treasure-island/game-ends, treasure-island/two-logs, treasure-island/story-record, treasure-island/toggles, treasure-island/no-token-strategies, treasure-island/no-vision, treasure-island/actions, runs/paced-from-cache, runs/same-in-every-process
"""

import json
import time
from itertools import groupby
from pathlib import Path

from treasure_island.brain import PirateSeat
from treasure_island.event_log import log_errors
from treasure_island.game_state import GameState
from treasure_island.pirates_log import PiratesLog
from treasure_island.score import score


def _surroundings(neighbours, dug):
    """What a pirate saw around it, for its turn's line of the story."""
    ground = "on dug sand" if dug else "on undug sand"
    beside = " and ".join(
        f"{name} to the {direction}" for direction, name in neighbours
    )
    return (
        f"{ground}, with {beside}" if beside else f"{ground}, with no pirate beside it"
    )


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


def _one_line(text):
    return " ".join(text.split())


def _lines_said(lines):
    """Scroll lines in plain words, with their numbers and writers, on one line."""
    return ", ".join(
        f'line {line["line"]} by {line["by"]} "{_one_line(line["text"])}"'
        for line in lines
    )


def _square(position):
    return f"({position[0]}, {position[1]})"


def _with_refusals(refused, did):
    """What a turn did, after any moves that were refused."""
    said = []
    for (action, why), tries in groupby(refused):
        count = len(list(tries))
        times = f" {count} times" if count > 1 else ""
        said.append(f"tried to move {action['direction']}{times} but {why}")
    if not said:
        return did
    return ", then ".join(said) + (f", then {did}" if did else ", so its turn passed")


class Game:
    def __init__(self, config, brains):
        if len(brains) != config.crew_size:
            raise ValueError(
                f"The config has {config.crew_size} pirates but {len(brains)} brains."
            )
        self.config = config
        self.state = GameState(config.grid_size, config.crew_size, config.seed)
        self.log = PiratesLog()
        self.names = [f"pirate-{number + 1}" for number in range(config.crew_size)]
        self._minds = [_Recording(brain) for brain in brains]
        self._seats = [
            PirateSeat(name, mind, config)
            for name, mind in zip(self.names, self._minds, strict=True)
        ]
        self._found_this_turn = False

    def records(self):
        """One record per turn, the last carrying `game_over`."""
        turns = self.config.crew_size * self.config.turns_per_pirate
        for turn in range(turns):
            record, moves_left = self._turn(turn)
            everyone_there = self._everyone_on_the_treasure()
            if everyone_there or turn == turns - 1:
                moves = moves_left if everyone_there else 0
                record["game_over"] = self._game_over(everyone_there, moves)
                yield record
                return
            yield record

    def _everyone_on_the_treasure(self):
        state = self.state
        return state.treasure_dug_up and all(
            position == state.treasure for position in state.positions
        )

    def _game_over(self, everyone_there, moves_remaining):
        state = self.state
        reason = (
            "everyone is on the treasure" if everyone_there else "the turns ran out"
        )
        final = score(
            state.positions, state.treasure, state.treasure_dug_up, moves_remaining
        )
        dug = "was dug up" if state.treasure_dug_up else "was never dug up"
        return {
            "reason": reason,
            "score": final,
            "moves_remaining": moves_remaining,
            "treasure": list(state.treasure),
            "treasure_dug_up": state.treasure_dug_up,
            "story": (
                f"Game over: {reason}. The treasure at {_square(state.treasure)} "
                f"{dug}. Score {final}, with {moves_remaining} moves to spare."
            ),
        }

    def _turn(self, turn):
        pirate = self.state.current_pirate
        name = self.names[pirate]
        start = self.state.positions[pirate]
        turns_left = self.config.turns_per_pirate - turn // self.config.crew_size
        crew = {
            crew_name: list(position)
            for crew_name, position in zip(
                self.names, self.state.positions, strict=True
            )
        }
        self._found_this_turn = False
        around = tuple(
            (direction, self.names[index])
            for direction, index in self.state.neighbours(pirate)
        )
        dug_here = start in self.state.dug
        seat, refused, bad_replies = self._seats[pirate], [], []
        while True:
            decision = seat.take_turn(start, turns_left, around, dug_here)
            bad_replies += decision.refused
            refusal = self._refusal(decision.action)
            if refusal is None:
                result, did, read_lines = self._act(decision.action, start, name)
                done = [decision.action] if decision.action else []
                break
            told, why = refusal
            refused.append((decision.action, why))
            if len(refused) < self.config.failed_tries:
                seat.remember(f"{told} That didn't use your turn: choose again.")
                continue
            # A brain that keeps choosing a failed action loses the turn instead.
            self.state.pass_turn()
            result = f"{told} That was your last try, so your turn passed."
            did, read_lines, done = "", [], []
            break
        seat.remember(result, read_lines)
        did = _with_refusals(refused, did)
        story = f"Turn {turn}: {name} at {_square(start)}, "
        story += f"{_surroundings(around, dug_here)}, {did}."
        if decision.thinking:
            story += f" Why: {_one_line(decision.thinking)}"
        record = {
            "turn": turn,
            "agent": name,
            "story": story,
            "happened": f"{did}.",
            "did": done,
            **({"failed_moves": [action for action, _ in refused]} if refused else {}),
            "result": result,
            "outcome": {
                "position": list(self.state.positions[pirate]),
                "found_treasure": self._found_this_turn,
            },
            "log_shown": read_lines,
            "crew": crew,
            "saw": {
                "position": list(start),
                "prompt": self._minds[pirate].prompt,
                "neighbours": dict(around),
                "square_dug": dug_here,
            },
        }
        if decision.thinking:
            record["thinking"] = decision.thinking
        if bad_replies:
            record["refused"] = bad_replies
        return record, turns_left - 1

    def _refusal(self, action):
        """What the pirate is told and the story's reason if its move can't happen."""
        if not action or action["action"] != "move":
            return None
        refused = self.state.refusal(action["direction"])
        if refused is None:
            return None
        if refused.blocked_by is None:
            edge = "edge" in refused.message
            why = "it was at the grid's edge" if edge else "there's no such direction"
            return refused.message, why
        blocker = self.names[refused.blocked_by]
        x, y = self.state.positions[refused.blocked_by]
        told = f"You can't move {action['direction']}: {blocker} is standing on ({x}, {y})."
        return told, f"{blocker} was in the way"

    def _act(self, action, start, name):
        """Do the action; return what the pirate is told, a story and lines read."""
        if action is None:
            self.state.pass_turn()
            told = "Your answers weren't tool calls, so your turn passed."
            return told, "passed, since its answers weren't tool calls", []
        return getattr(self, f"_{action['action']}")(action, start, name)

    def _move(self, action, start, name):
        direction = action["direction"]
        result = self.state.move(direction)  # refused moves never get this far
        end = self.state.positions[self.state.current_pirate - 1]
        return result.message, f"moved {direction} to {_square(end)}", []

    def _dig(self, action, start, name):
        result = self.state.dig()
        if result.found_treasure:
            self._found_this_turn = True
            return result.message, f"dug at {_square(start)} and found the treasure", []
        return result.message, f"dug at {_square(start)} and found nothing", []

    def _write(self, action, start, name):
        self.log.write(name, action["text"])
        self.state.pass_turn()
        note = _one_line(action["text"])
        return f'You wrote on the scroll: "{note}".', f'wrote "{note}"', []

    def _read(self, action, start, name):
        answer = self.log.read(name)
        self.state.pass_turn()
        if not answer.lines:
            return answer.message, "read the scroll and found nothing new", []
        return (
            "You read the scroll.",
            f"read the scroll and found {_lines_said(answer.lines)}",
            answer.lines,
        )


def write_game(config, brains, folder, pace=0):
    """Play a game into `folder`, as it happens, and return its `game_over`.

    A stopped game returns `{"stopped": why}` instead. `pace` waits that many
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
        story.write((ending["story"] + "\n").encode())
    scroll = "".join(
        f"{line['line']} {line['by']}: {line['text']}\n" for line in game.log.lines()
    )
    (folder / "pirates-log.txt").write_bytes(scroll.encode())
    if played and (errors := log_errors(folder / "events.jsonl")):
        raise ValueError("\n".join(errors))
    return ending
