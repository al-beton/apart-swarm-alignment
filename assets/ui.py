# Implements: assets/viewer-parts, assets/original-art
"""Viewer parts: a speech bubble, a side panel and the arrow for whose turn it is.

The bubble and panel are drawn as nine-slice images: fixed corners, stretched edges.
"""

from PIL import Image, ImageDraw

from assets.font import FONT_HEIGHT, FONT_WIDTH, draw_text, text_width, wrap
from assets.pixels import CREAM, DARK, OUTLINE, add_outline, rgba

BUBBLE_CELL = 8
PANEL_CELL = 12
_BUBBLE_PADDING = 6
_TAIL = 8


def bubble_slices():
    """A 24x24 nine-slice with 8px cells: cream on dark, rounded."""
    image = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    ImageDraw.Draw(image).rounded_rectangle(
        [0, 0, 23, 23], radius=4, fill=CREAM, outline=OUTLINE
    )
    return image


def bubble_tail():
    """12x8, placed under the bubble, pointing down at the speaker."""
    image = Image.new("RGBA", (12, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon([(1, 0), (9, 0), (3, 6)], fill=OUTLINE)
    draw.polygon([(2, 0), (8, 0), (4, 4)], fill=CREAM)
    return image


def panel_slices():
    """A 36x36 nine-slice with 12px cells: parchment in a wooden frame."""
    image = Image.new("RGBA", (36, 36), rgba("#6e4522"))
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 35, 35], outline=OUTLINE)
    draw.rectangle([1, 1, 34, 1], fill="#a87038")
    draw.rectangle([1, 1, 1, 34], fill="#a87038")
    draw.rectangle([4, 4, 31, 31], fill=OUTLINE)
    draw.rectangle([5, 5, 30, 30], fill="#f0e2bc")
    return image


def turn_arrow():
    """16x12, floated above the pirate whose turn it is."""
    image = Image.new("RGBA", (16, 12), (0, 0, 0, 0))
    ImageDraw.Draw(image).polygon([(1, 1), (14, 1), (8, 9), (7, 9)], fill="#ffd84a")
    add_outline(image)
    return image


def _stretch(slices, cell, width, height):
    """Builds a width x height image from a nine-slice with the given cell size."""
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    columns = [(0, cell, 0, cell), (cell, cell, cell, width - 2 * cell)]
    columns.append((2 * cell, cell, width - cell, cell))
    rows = [(0, cell, 0, cell), (cell, cell, cell, height - 2 * cell)]
    rows.append((2 * cell, cell, height - cell, cell))
    for sx, sw, dx, dw in columns:
        for sy, sh, dy, dh in rows:
            part = slices.crop((sx, sy, sx + sw, sy + sh))
            out.paste(part.resize((dw, dh), Image.NEAREST), (dx, dy))
    return out


def panel(width, height):
    """The side panel or log frame at any size of at least 24x24."""
    return _stretch(panel_slices(), PANEL_CELL, width, height)


def speech_bubble(text, max_width=168):
    """A bubble that fits text, tail included; the tail tip is near the bottom left."""
    columns = max(1, (max_width - 2 * _BUBBLE_PADDING) // FONT_WIDTH)
    lines = wrap(text, columns)
    width = max(text_width(line) for line in lines) + 2 * _BUBBLE_PADDING
    width = max(width, 3 * BUBBLE_CELL)
    body = len(lines) * FONT_HEIGHT + 2 * _BUBBLE_PADDING - 1
    body = max(body, 3 * BUBBLE_CELL)
    image = Image.new("RGBA", (width, body + _TAIL), (0, 0, 0, 0))
    image.paste(_stretch(bubble_slices(), BUBBLE_CELL, width, body), (0, 0))
    image.alpha_composite(bubble_tail(), (6, body - 1))
    for i, line in enumerate(lines):
        draw_text(
            image, (_BUBBLE_PADDING, _BUBBLE_PADDING + i * FONT_HEIGHT), line, DARK
        )
    return image
