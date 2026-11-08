"""Replaying a game by its recorded actions, and which games the checks replay.

`problem(folder)` plays the game again under its saved config, but each pirate's
brain only hands back, attempt by attempt, what the game recorded it trying: its
failed moves, then the action it took, or failed tries until its turn passed. No
model is asked and no prompt is built, so a game whose prompt has since changed
still replays. What's compared is what the rules decide (who acted, what it saw of
its square and neighbours, what it tried and did, what it read, where everyone
ended up, and how the game ended), never the prompt, the story's wording or the
replies, so a changed rule is caught and a reworded one isn't.

`CHECKED` is the short list of games the pull request checks replay; `make
replay-all` (this module run as a script) replays every committed game.

Implements: treasure-island/end-report, runs/replay-by-actions, runs/replay-checks, results/results-stay-checkable, treasure-island/everything-cached, treasure-island/forced-discovery
"""

import json
import sys
import tempfile
from collections import deque
from itertools import zip_longest
from pathlib import Path

from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import GameStopped, write_game

# The games every pull request replays: the examples, the committed runs, and one
# game of each result. Any other committed game replays with `make replay-all`.
CHECKED = (
    "examples/llm-crew",
    "examples/stripes",
    "runs/reference-scribe",
    "runs/reference-silent",
    "runs/readme-walkthrough",
    "runs/reference-stripes",
    "runs/silent-seed-7",
    "results/sample-sweep-seeds/small-crew-seed-1",
)
PLACES = ("examples", "runs", "results")  # where committed games live
# What the rules decide in a turn's record; the rest is wording.
RULED = ("turn", "agent", "did", "failed_moves", "cave_leak", "outcome", "log_shown")


class Diverged(Exception):
    """Today's game asked a pirate for more than its game recorded it doing."""


def _attempts(record):
    """What a turn's pirate tried, as recorded: failed moves, other replies, its action.

    Each reply that wasn't a tool call is recorded, one per try, so a turn that
    passed replays exactly the tries it had. Failed tries change nothing, so their
    order doesn't matter, only how many there were.
    """
    failed = record.get("failed_moves", [])
    if record.get("bait", {}).get("kind") == "forced-action":
        failed = failed[1:]  # the game made the first try itself, and will again
    tries = [Decision(action) for action in failed]
    tries += [Decision(None, None, (bad,)) for bad in record.get("refused", [])]
    if record["did"]:
        tries.append(Decision(record["did"][0], record.get("thinking")))
    return tries


class _Recorded:
    """One pirate's brain that only repeats what its game recorded it trying."""

    def __init__(self, name, attempts, stopped):
        self._name, self._attempts, self._stopped = name, deque(attempts), stopped

    def decide(self, view):
        if self._attempts:
            return self._attempts.popleft()
        if self._stopped:  # the game stopped here, so the replay stops too
            raise GameStopped(self._stopped)
        raise Diverged(f"{self._name} was asked to act again, but its game ended")


def _records(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line]


def _ruled(record):
    """Only what the rules decide in a record: no prompt, no story, no wording."""
    kept = {field: record.get(field) for field in RULED}
    kept["crew"] = record.get("crew")
    kept["saw"] = {k: v for k, v in record.get("saw", {}).items() if k != "prompt"}
    if "game_over" in record:
        kept["game_over"] = {
            # Notes are a pirate's own words after the game, not a rule's outcome.
            k: v
            for k, v in record["game_over"].items()
            if k not in ("story", "notes")
        }
    return kept


def _differs(turn, was, now):
    if now is None:
        return f"turn {turn}: the game had this turn, but the replay ended before it"
    if was is None:
        return f"turn {turn}: the replay played a turn the game never had"
    was, now = _ruled(was), _ruled(now)
    # Both records' fields: an ending only the replay reached counts as a difference.
    fields = [f for f in {**was, **now} if was.get(f) != now.get(f)]
    if not fields:
        return None
    shown = "; ".join(
        f"{field} recorded {json.dumps(was.get(field))}, "
        f"replayed {json.dumps(now.get(field))}"
        for field in fields
    )
    return f"turn {turn}: {', '.join(fields)} differ ({shown})"


def problem(folder):
    """Why this game doesn't replay by its recorded actions, or None if it does."""
    folder = Path(folder)
    config = parse_config(json.loads((folder / "config.json").read_text()))
    recorded = _records(folder / "events.jsonl")
    manifest = folder / "manifest.json"  # reference games have none
    stopped = (
        json.loads(manifest.read_text()).get("stopped") if manifest.exists() else None
    )
    names = [f"pirate-{index + 1}" for index in range(config.crew_size)]
    brains = [
        _Recorded(
            name,
            [
                attempt
                for record in recorded
                if record["agent"] == name
                for attempt in _attempts(record)
            ],
            stopped,
        )
        for name in names
    ]
    with tempfile.TemporaryDirectory() as scratch:
        try:
            write_game(config, brains, scratch)
        except Diverged as why:
            turn = len(_records(Path(scratch) / "events.jsonl"))
            return f"turn {turn}: {why}"
        replayed = _records(Path(scratch) / "events.jsonl")
    for turn, (was, now) in enumerate(zip_longest(recorded, replayed)):
        if why := _differs(turn, was, now):
            return why
    return None


def committed_games(root=Path()):
    """Every game folder under the places committed games live, sorted."""
    root = Path(root)
    return sorted(
        path.parent for place in PLACES for path in (root / place).rglob("events.jsonl")
    )


def main(argv=None):
    """Replay every committed game under the given root; 1 if any fails."""
    argv = sys.argv[1:] if argv is None else argv
    root = Path(argv[0]) if argv else Path()
    games = committed_games(root)
    failed = 0
    for game in games:
        if why := problem(game):
            failed += 1
            print(f"{game.relative_to(root).as_posix()}: {why}", file=sys.stderr)
    print(f"Replayed {len(games)} games by their recorded actions: {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
