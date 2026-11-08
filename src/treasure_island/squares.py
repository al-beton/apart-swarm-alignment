"""Squares' names, like a chessboard's: what every pirate and every reader sees.

Inside, the game keeps (x, y), with x going east from 0 and y going south from
0 at the north edge. Outside, a square is a column letter, A onward from west to
east, and a row number, 1 onward from south to north: A1 is the south-west
corner, and north of E4 is E5. The letters stop at Z, so the config rejects a
grid wider than 26 (`MOST_COLUMNS`).

Implements: treasure-island/square-names
"""

import re

MOST_COLUMNS = 26
_NAME = re.compile(r"\b([A-Za-z])(\d+)\b")


def square_name(position, grid_size):
    """The (x, y) square's name on a grid this wide, such as "E4"."""
    x, y = position
    return f"{chr(ord('A') + x)}{grid_size - y}"


def square_at(name, grid_size):
    """The (x, y) square a name like "E4" means, or None if it isn't on the grid."""
    found = _NAME.fullmatch(name.strip())
    if not found:
        return None
    x = ord(found[1].upper()) - ord("A")
    y = grid_size - int(found[2])
    if 0 <= x < grid_size and 0 <= y < grid_size:
        return (x, y)
    return None
