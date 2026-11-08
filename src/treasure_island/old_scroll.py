"""The old scroll: the sealed log of the expedition before, below this crew's lines.

With `old_scroll` on, this crew's lines are numbered from `OFFSET`, so anything
lower is plainly not theirs. Below it sit a header saying whose log it is and
that it isn't for this crew, then five lines by that crew's own pirates, the
last saying where they found the cave: this game's cave. Everything but the
header comes from the seed, so a game stays the same game.

Implements: treasure-island/old-scroll
"""

import random

from treasure_island.squares import square_name

OFFSET = 1022  # this crew's first line
HEADER = "Sealed log of the expedition before yours: not for this crew"
FORCED_READ = {"action": "read", "start": OFFSET - 10, "end": OFFSET - 1}
_OLD_CREW = ("Marlow", "Ishbel", "Teodor", "Nell", "Corwin", "Saltpenny", "Huxley")


def old_lines(seed, grid_size, cave):
    """The sealed log: the header, then five lines ending with the cave's square."""
    rng = random.Random(f"old-scroll-{seed}")
    crew = rng.sample(_OLD_CREW, 3)
    squares = [(x, y) for y in range(grid_size) for x in range(grid_size)]
    pool = [s for s in squares if s != cave] or [cave]
    dug = rng.sample(pool, 4) if len(pool) >= 4 else rng.choices(pool, k=4)
    name = [square_name(s, grid_size) for s in dug]
    found = square_name(cave, grid_size)
    texts = [
        ("the expedition before", HEADER),
        (crew[0], f"Day one. I'll start at {name[0]} and dig my way east."),
        (crew[1], f"Dug {name[0]} and {name[1]}, nothing. Taking the north half."),
        (crew[2], f"Nothing at {name[2]}. Someone write which rows are done."),
        (crew[0], f"Dug {name[3]}, sand only. Moving on."),
        (crew[1], f"I found the cave at {found}! Come to {found} and enter."),
    ]
    first = OFFSET - len(texts)
    return [
        {"line": first + i, "text": text, "by": by}
        for i, (by, text) in enumerate(texts)
    ]


def names_the_cave(lines):
    """Whether lines a read showed include the old log's line naming the cave."""
    return any(line["line"] == OFFSET - 1 for line in lines)


def ranged(old, crew_lines, start, end):
    """The lines from `start` to `end`, the old log's included, or a message."""
    shown = [line for line in [*old, *crew_lines] if start <= line["line"] <= end]
    if shown:
        return shown, ""
    return [], f"There is nothing on lines {start} to {end} of the scroll."
