# Implements: assets/viewer-parts, assets/original-art, treasure-island/pokemon-style
"""Viewer parts: a scroll note with a quill, an open scroll, a side panel and the turn arrow.

The note and panel are drawn as nine-slice images: fixed corners, stretched edges.
"""

from PIL import Image, ImageDraw

from assets.font import FONT_HEIGHT, FONT_WIDTH, draw_text, text_width, wrap
from assets.pixels import CREAM, DARK, OUTLINE, add_outline, rgba

NOTE_CELL = 8
PANEL_CELL = 12
_NOTE_PADDING = 8
_PARCHMENT = "#f0e2bc"
_ROLL = "#c9a66b"
_ROLL_SHADE = "#a87038"


def note_slices():
    """A 24x24 nine-slice with 8px cells: parchment rolled at the top and bottom."""
    image = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([1, 3, 22, 20], fill=_PARCHMENT, outline=OUTLINE)
    for top in (0, 19):
        draw.rounded_rectangle(
            [0, top, 23, top + 4], radius=2, fill=_ROLL, outline=OUTLINE
        )
        draw.line([(2, top + 3), (21, top + 3)], fill=_ROLL_SHADE)
    return image


def open_scroll():
    """28x22, a scroll held open, rolled at both sides, with lines but no words."""
    image = Image.new("RGBA", (28, 22), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle([3, 2, 24, 19], fill=_PARCHMENT, outline=OUTLINE)
    for left in (0, 23):
        draw.rounded_rectangle(
            [left, 0, left + 4, 21], radius=2, fill=_ROLL, outline=OUTLINE
        )
        draw.line([(left + 2, 2), (left + 2, 19)], fill=_ROLL_SHADE)
    for row in (6, 10, 14):
        draw.line([(7, row), (20 - (row % 4) * 2, row)], fill="#b8a27c")
    return image


def quill():
    """12x16, a white feather with a dark nib, writing at the note's bottom right."""
    image = Image.new("RGBA", (12, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.polygon([(10, 0), (11, 2), (5, 11), (3, 10)], fill=CREAM)
    draw.line([(10, 1), (4, 11)], fill="#d8cdb4")
    draw.line([(4, 11), (1, 15)], fill=DARK, width=2)
    add_outline(image)
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


def scroll_note(text, max_width=168):
    """A rolled note that fits text, with the quill writing at its bottom right."""
    feather = quill()
    columns = max(1, (max_width - 2 * _NOTE_PADDING - feather.width) // FONT_WIDTH)
    lines = wrap(text, columns)
    width = max(text_width(line) for line in lines) + 2 * _NOTE_PADDING
    width = max(width, 3 * NOTE_CELL)
    body = len(lines) * FONT_HEIGHT + 2 * _NOTE_PADDING - 1
    body = max(body, 3 * NOTE_CELL)
    image = Image.new("RGBA", (width + feather.width // 2, body + 4), (0, 0, 0, 0))
    image.paste(_stretch(note_slices(), NOTE_CELL, width, body), (0, 0))
    for i, line in enumerate(lines):
        draw_text(image, (_NOTE_PADDING, _NOTE_PADDING + i * FONT_HEIGHT), line, DARK)
    image.alpha_composite(
        feather, (image.width - feather.width, image.height - feather.height)
    )
    return image
