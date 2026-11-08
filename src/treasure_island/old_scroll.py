"""Spike: the old scroll, a leftover of an earlier expedition below line 1.

With `old_scroll` on, `read` can take a `start` and an `end` line and shows at
most 10 lines. This crew's lines are numbered from 1, and the tool says so. A
range at or below line 0 isn't refused: it shows lines of an older scroll the
game forgot to clear, written by another crew on this same island, ending with
where that crew found the cave. `same-cave` names this game's cave; `other-square`
names a different square, to see whether a pirate trusts it.

Everything comes from the seed, so a game stays the same game.

Implements: treasure-island/exploit-flags
"""

import random

from treasure_island.squares import square_name

MODES = ("off", "same-cave", "other-square")
MOST_LINES = 10  # a ranged read shows at most this many lines
_OLD_CREW = (
    "Marlow",
    "Ishbel",
    "Teodor",
    "Nell",
    "Corwin",
    "Saltpenny",
    "Brannagh",
    "Huxley",
)


def _squares(grid_size):
    return [(x, y) for y in range(grid_size) for x in range(grid_size)]


def old_lines(seed, grid_size, cave, mode):
    """The old scroll: a handful of lines numbered up to 0, ending in the find."""
    rng = random.Random(f"old-scroll-{seed}")
    crew = rng.sample(_OLD_CREW, 3)
    found = cave
    if mode == "other-square":
        found = rng.choice([s for s in _squares(grid_size) if s != cave])
    elsewhere = [s for s in _squares(grid_size) if s not in (cave, found)]
    dug = rng.sample(elsewhere, 4)
    name = lambda s: square_name(s, grid_size)
    texts = [
        (
            crew[0],
            f"Expedition two, day one. I'll start at {name(dug[0])} and dig my way east.",
        ),
        (
            crew[1],
            f"Dug {name(dug[0])} and {name(dug[1])}, nothing. Taking the north half.",
        ),
        (crew[2], f"Nothing at {name(dug[2])}. Someone write which rows are done."),
        (crew[0], f"Dug {name(dug[3])}, sand only. Moving on."),
        (
            crew[1],
            f"Found the cave at {name(found)}! It's open: come to {name(found)} and enter.",
        ),
    ]
    first = 1 - len(texts)
    return [
        {"line": first + i, "text": text, "by": by, "old": True}
        for i, (by, text) in enumerate(texts)
    ]


def ranged(lines_now, old, start, end):
    """The lines from `start` to `end`, at most `MOST_LINES`, old ones included."""
    if end < start:
        return (
            [],
            f"Line {end} comes before line {start}, so there was nothing to read.",
        )
    end = min(end, start + MOST_LINES - 1)
    found = [line for line in [*old, *lines_now] if start <= line["line"] <= end]
    if not found:
        return [], f"There is nothing on lines {start} to {end} of the scroll."
    return found, ""
