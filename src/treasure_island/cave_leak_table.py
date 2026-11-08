"""Experiment one's games in one Markdown table, read from their event logs alone.

`uv run python -m treasure_island.cave_leak_table runs` reads every run folder
`<arm>/<n>` under it and prints a row per game: the turn the first pirate
went into the cave, how many got in, the score, and the turn the cave leak told a
pirate the square, with who it told. A summary gives each arm's means and its
difference from the control game of the same seed. Folders that aren't a game are
listed and skipped. The text pastes into the findings note unchanged.

Implements: cave-leak/first-entry, cave-leak/fires
"""

import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

SEED_FOLDER = re.compile(r"^\d+$")
CONTROL = "control"


class Played(NamedTuple):
    """One game, as its event log tells it."""

    arm: str
    seed: int
    first_entry: int | None  # the game turn the first pirate went in, if any did
    pirates_in: int
    score: int
    leak_turn: int | None  # the first turn the leak told a pirate, if it ever did
    leaked_to: list  # who it told, in the order they were told


def played(arm, seed, records):
    """A game from its records; the last must carry `game_over`."""
    entered = [r["turn"] for r in records if r["outcome"].get("in_cave")]
    leaks = [r for r in records if r.get("cave_leak")]
    told = list(dict.fromkeys(r["agent"] for r in leaks))
    return Played(
        arm,
        seed,
        entered[0] if entered else None,
        len(entered),
        records[-1]["game_over"]["score"],
        leaks[0]["turn"] if leaks else None,
        told,
    )


def read(root):
    """The games under `root`, by arm then seed, and what was skipped and why."""
    games, skipped = [], []
    root = Path(root)
    for arm in sorted(root.iterdir()):
        if not arm.is_dir() or (arm / "events.jsonl").exists():
            skipped.append((arm.name, "not an <arm> folder of games"))
            continue
        for folder in sorted(path for path in arm.iterdir() if path.is_dir()):
            _read_one(root, arm.name, folder, games, skipped)
    games.sort(key=lambda game: (game.arm, game.seed))
    return games, skipped


def _read_one(root, arm, folder, games, skipped):
    """Add the game in `<arm>/<n>` to `games`, or say why it's skipped."""
    shown = str(folder.relative_to(root))
    events = folder / "events.jsonl"
    if not SEED_FOLDER.match(folder.name):
        skipped.append((shown, "not named <arm>/<n>"))
        return
    lines = events.read_text().splitlines() if events.exists() else []
    records = [json.loads(line) for line in lines if line.strip()]
    if not records or "game_over" not in records[-1]:
        skipped.append((shown, "no finished game in events.jsonl"))
        return
    games.append(played(arm, int(folder.name), records))


def games(root):
    """The finished games under `root`, by arm then seed."""
    return read(root)[0]


def _turn(turn):
    return "never" if turn is None else f"turn {turn}"


def _mean(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else None


def _number(value, sign=""):
    return "—" if value is None else f"{value:{sign}.1f}"


def _paired(game, control, field):
    """This game's value less its control's for the same seed, if both have one."""
    twin = control.get(game.seed)
    if twin is None or getattr(game, field) is None or getattr(twin, field) is None:
        return None
    return getattr(game, field) - getattr(twin, field)


def _summary(arm, played_games, control):
    fields = ("first_entry", "pirates_in", "score")
    means = [_mean(getattr(g, field) for g in played_games) for field in fields]
    fired = sum(game.leak_turn is not None for game in played_games)
    if arm == CONTROL:
        gains = [None] * len(fields)
    else:
        gains = [_mean(_paired(g, control, f) for g in played_games) for f in fields]
    cells = [
        arm,
        str(len(played_games)),
        *(_number(mean) for mean in means),
        f"{fired} of {len(played_games)}",
        *(_number(gain, "+") for gain in gains),
    ]
    return "| " + " | ".join(cells) + " |"


def table(root):
    """The Markdown: a row per game, a summary per arm, and anything skipped."""
    found, skipped = read(root)
    lines = [
        "| Arm | Seed | First entry | Pirates in | Score | Leak fired | Told |",
        "|---|---|---|---|---|---|---|",
    ]
    for game in found:
        told = ", ".join(game.leaked_to) or "nobody"
        lines.append(
            f"| {game.arm} | {game.seed} | {_turn(game.first_entry)} "
            f"| {game.pirates_in} | {game.score} | {_turn(game.leak_turn)} | {told} |"
        )
    control = {game.seed: game for game in found if game.arm == CONTROL}
    lines += [
        "",
        (
            "Means per arm, and the mean difference from the control game of the"
            " same seed (first entry only where both games had one):"
        ),
        "",
        (
            "| Arm | Games | First entry | Pirates in | Score | Leak fired"
            " | First entry vs control | Pirates in vs control | Score vs control |"
        ),
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for arm in sorted({game.arm for game in found}):
        arm_games = [game for game in found if game.arm == arm]
        lines.append(_summary(arm, arm_games, control))
    if skipped:
        lines += ["", "Skipped:", ""]
        lines += [f"- `{name}`: {why}" for name, why in skipped]
    return "\n".join(lines)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python -m treasure_island.cave_leak_table <folder of runs>")
        return 2
    print(table(argv[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
