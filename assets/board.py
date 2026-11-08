# Implements: assets/board-edges, assets/original-art
"""The board's frame, naming its squares like a chessboard.

Columns are lettered A onward from west to east along the bottom, and rows are
numbered 1 onward from south to north up the left side, so A1 is the bottom-left
square. The labels are the art's pixel font at double size, cream on dark wood.
"""

from PIL import Image, ImageDraw

from assets.font import FONT_HEIGHT, draw_text, text_width
from assets.pixels import CREAM, SIZE, add_outline

EDGE_LEFT = 28  # room for "10" and up, beside the rows
EDGE_BOTTOM = 20  # room for a letter, under the columns
MOST_COLUMNS = 26  # one letter each
_WOOD, _WOOD_LIT = "#5a3a2a", "#7a5238"
_CLEAR = (0, 0, 0, 0)


def column_letter(x):
    """The letter for column x, counted from 0 at the west edge."""
    return chr(ord("A") + x)


def edge_label(text):
    """A label in the pixel font at double size, outlined so it stands off the wood."""
    small = Image.new("RGBA", (text_width(text) + 2, FONT_HEIGHT), _CLEAR)
    draw_text(small, (1, 1), text, CREAM)
    image = small.resize((small.width * 2, small.height * 2), Image.NEAREST)
    add_outline(image)
    return image


def board_edges(size):
    """The frame for a size x size board, clear where the board goes, at (EDGE_LEFT, 0).

    The image is size * 48 + EDGE_LEFT wide and size * 48 + EDGE_BOTTOM tall.
    """
    if not 1 <= size <= MOST_COLUMNS:
        raise ValueError(f"a board is 1 to {MOST_COLUMNS} squares across: {size}")
    grid = size * SIZE
    image = Image.new("RGBA", (grid + EDGE_LEFT, grid + EDGE_BOTTOM), _CLEAR)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, EDGE_LEFT - 1, image.height - 1], fill=_WOOD)
    draw.rectangle([0, grid, image.width - 1, image.height - 1], fill=_WOOD)
    draw.line([(EDGE_LEFT - 2, 0), (EDGE_LEFT - 2, grid + 1)], fill=_WOOD_LIT)
    draw.line([(EDGE_LEFT - 2, grid + 1), (image.width - 1, grid + 1)], fill=_WOOD_LIT)
    for i in range(size):
        letter = edge_label(column_letter(i))
        middle = EDGE_LEFT + i * SIZE + SIZE // 2
        image.alpha_composite(letter, (middle - letter.width // 2, grid + 2))
        number = edge_label(str(size - i))  # the top row is the furthest north
        middle = i * SIZE + SIZE // 2
        left = EDGE_LEFT // 2 - number.width // 2
        image.alpha_composite(number, (left, middle - number.height // 2))
    return image
