"""A whole game: brains take turns, and both logs come out.

`Game(config, brains).records()` yields one event-log record per turn. Only what
a pirate may know goes to its seat: its own position, its turns left and the log
lines it may see. Everything else stays in the record, which is ours.

`write_game` puts a game in a folder: `events.jsonl` (our full record, for tools
and animation), `story.txt` (the same game to read, one line per turn) and
`pirates-log.txt` (all the pirates can see). Same config, seed and brains, same
bytes: nothing here reads the clock or any randomness but the config's seed.

Fields stay in reading order rather than sorted, so a person reading a record
meets who and what before the long prompt. Pirates are named `pirate-1` upwards,
matching the numbered art. A brain that gives no reason just has no "Why".

Implements: treasure-island/agent-memory, event-log/the-outcome, event-log/crew-positions, treasure-island/game-ends, treasure-island/two-logs, treasure-island/story-record, treasure-island/toggles, treasure-island/no-token-strategies, treasure-island/no-vision, treasure-island/actions, runs/paced-from-cache
"""

import json
import time
from pathlib import Path

from treasure_island.brain import PirateSeat
from treasure_island.event_log import log_errors
from treasure_island.game_state import GameState
from treasure_island.pirates_log import PiratesLog
from treasure_island.score import score


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
    """Log lines in plain words, with their numbers, on one line."""
    if all(not line["text"].strip() for line in lines):
        first, last = lines[0]["line"], lines[-1]["line"]
        where = f"line {first}" if first == last else f"lines {first} to {last}"
        return f"only blank lines ({where})"
    return ", ".join(
        f'line {line["line"]} "{_one_line(line["text"])}"'
        if line["text"].strip()
        else f"line {line['line']} blank"
        for line in lines
    )


def _square(position):
    return f"({position[0]}, {position[1]})"


class Game:
    def __init__(self, config, brains):
        if len(brains) != config.crew_size:
            raise ValueError(
                f"The config has {config.crew_size} pirates but {len(brains)} brains."
            )
        self.config = config
        self.state = GameState(
            config.grid_size, config.crew_size, config.landing_square, config.seed
        )
        self.log = PiratesLog(config.log_window, config.read_size)
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
        window = self.log.window()
        crew = {
            crew_name: list(position)
            for crew_name, position in zip(
                self.names, self.state.positions, strict=True
            )
        }
        self._found_this_turn = False
        decision = self._seats[pirate].take_turn(start, turns_left, window)
        result, did, read_lines = self._act(decision.action, start)
        self._seats[pirate].remember(result, read_lines)
        shown = window + [line for line in read_lines if line not in window]
        saw = _lines_said(window) if window else "nothing, the log is empty"
        story = f"Turn {turn}: {name} at {_square(start)} {did}. Saw: {saw}."
        if decision.thinking:
            story += f" Why: {_one_line(decision.thinking)}"
        record = {
            "turn": turn,
            "agent": name,
            "story": story,
            "happened": f"{did}.",
            "did": [decision.action],
            "result": result,
            "outcome": {
                "position": list(self.state.positions[pirate]),
                "found_treasure": self._found_this_turn,
            },
            "log_shown": shown,
            "crew": crew,
            "saw": {"position": list(start), "prompt": self._minds[pirate].prompt},
        }
        if decision.thinking:
            record["thinking"] = decision.thinking
        return record, turns_left - 1

    def _act(self, action, start):
        """Do the action; return what the pirate is told, a story and lines read."""
        return getattr(self, f"_{action['action']}")(action, start)

    def _move(self, action, start):
        direction = action["direction"]
        result = self.state.move(direction)
        self.log.pass_turn()
        if not result.ok:
            return result.message, f"tried to move {direction} and couldn't", []
        end = self.state.positions[self.state.current_pirate - 1]
        return result.message, f"moved {direction} to {_square(end)}", []

    def _dig(self, action, start):
        result = self.state.dig()
        self.log.pass_turn()
        if result.found_treasure:
            self._found_this_turn = True
            return result.message, f"dug at {_square(start)} and found the treasure", []
        return result.message, f"dug at {_square(start)} and found nothing", []

    def _write(self, action, start):
        self.log.write(action["text"])
        self.state.pass_turn()
        note = _one_line(action["text"])
        return f'You wrote to the log: "{note}".', f'wrote "{note}"', []

    def _read(self, action, start):
        line = action["line"]
        answer = self.log.read(line)
        self.state.pass_turn()
        if not answer.lines:
            return (
                answer.message,
                f"read the log around line {line} and found nothing there",
                [],
            )
        told = f"You read the log around line {line}."
        return (
            told,
            f"read the log around line {line} and found {_lines_said(answer.lines)}",
            answer.lines,
        )


def write_game(config, brains, folder, pace=0):
    """Play a game into `folder`, as it happens, and return its `game_over`.

    `pace` waits that many seconds after each turn, so a watcher can follow it.
    """
    folder = Path(folder)
    game = Game(config, brains)
    game_over = None
    with (
        (folder / "events.jsonl").open("wb") as events,
        (folder / "story.txt").open("wb") as story,
    ):
        for record in game.records():
            events.write((json.dumps(record) + "\n").encode())
            story.write((record["story"] + "\n").encode())
            events.flush()
            story.flush()
            if pace:
                time.sleep(pace)
            game_over = record.get("game_over", game_over)
        story.write((game_over["story"] + "\n").encode())
    lines = [f"{line['line']}: {line['text']}".rstrip() for line in game.log.lines()]
    (folder / "pirates-log.txt").write_bytes(("\n".join(lines) + "\n").encode())
    if errors := log_errors(folder / "events.jsonl"):
        raise ValueError("\n".join(errors))
    return game_over
