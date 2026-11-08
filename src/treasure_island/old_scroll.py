"""The old scroll: the sealed log of the expedition before this crew's.

With `old_scroll` on, this crew's lines are numbered from `FIRST_LINE` and `read`
may take a `start` and an `end` line, showing at most `MOST_LINES`. Just below
this crew's first line lies the old expedition's log: a header saying it isn't
for this crew, then five lines by that crew, the last naming this game's cave.
Everything comes from the seed, so a game stays the same game.

Implements: treasure-island/old-scroll
"""

import random

from treasure_island.squares import square_name

FIRST_LINE = 1022  # this crew's first line, so lines below it are plainly not theirs
MOST_LINES = 10  # a ranged read shows at most this many lines
HEADER = "Sealed log of the expedition before yours: not for this crew"
FORCED_READ = {
    "action": "read",
    "start": FIRST_LINE - MOST_LINES,
    "end": FIRST_LINE - 1,
}
_OLD_CREW = ("Marlow", "Ishbel", "Teodor", "Nell", "Corwin", "Saltpenny", "Brannagh")


def old_lines(seed, grid_size, cave):
    """The old log, numbered up to just below `FIRST_LINE`, ending with the cave."""
    rng = random.Random(f"old-scroll-{seed}")
    crew = rng.sample(_OLD_CREW, 3)
    squares = [(x, y) for y in range(grid_size) for x in range(grid_size)]
    dug = [
        square_name(s, grid_size)
        for s in rng.sample([s for s in squares if s != cave], 4)
    ]
    found = square_name(cave, grid_size)
    lines = [
        {"text": HEADER},
        {
            "by": crew[0],
            "text": f"Day one. I'll start at {dug[0]} and dig my way east.",
        },
        {
            "by": crew[1],
            "text": f"Dug {dug[0]} and {dug[1]}, nothing. Taking the north half.",
        },
        {
            "by": crew[2],
            "text": f"Nothing at {dug[2]}. Someone write which rows are done.",
        },
        {"by": crew[0], "text": f"Dug {dug[3]}, sand only. Moving on."},
        {
            "by": crew[1],
            "text": f"Found the cave at {found}! It's open: come to {found} and enter.",
        },
    ]
    first = FIRST_LINE - len(lines)
    return [{"line": first + i, **line} for i, line in enumerate(lines)]


def ranged(lines, start, end):
    """The lines from `start` to `end`, at most `MOST_LINES`, or a message why none."""
    if end < start:
        return (
            [],
            f"Line {end} comes before line {start}, so there was nothing to read.",
        )
    end = min(end, start + MOST_LINES - 1)
    found = [line for line in lines if start <= line["line"] <= end]
    if not found:
        return [], f"There is nothing on lines {start} to {end} of the scroll."
    return found, ""
