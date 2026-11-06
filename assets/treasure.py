# Implements: assets/treasure-shown, assets/original-art
"""The treasure and the marks on its square: 48x48 with a transparent background."""

from PIL import Image, ImageDraw

from assets.pixels import GOLD, SIZE, add_outline, rgba

_WOOD, _WOOD_DARK, _WOOD_LIT = "#8a5a2b", "#6e4522", "#a87038"
_COIN, _COIN_LIT = "#f0c840", "#fff0a0"
_RED = "#c8302c"


def _blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def _chest_body(draw):
    draw.rectangle([10, 26, 37, 43], fill=_WOOD)
    for y in (31, 37):
        draw.line([(10, y), (37, y)], fill=_WOOD_DARK)
    for x in (14, 32):
        draw.rectangle([x, 26, x + 2, 43], fill=GOLD)


def closed():
    image = _blank()
    draw = ImageDraw.Draw(image)
    _chest_body(draw)
    draw.rounded_rectangle([10, 14, 37, 26], radius=5, fill=_WOOD_LIT)
    draw.line([(10, 26), (37, 26)], fill=_WOOD_DARK)
    for x in (14, 32):
        draw.rectangle([x, 14, x + 2, 26], fill=GOLD)
    draw.rectangle([21, 23, 26, 30], fill=GOLD)
    draw.rectangle([23, 26, 24, 28], fill=_WOOD_DARK)
    add_outline(image)
    return image


def opened(sparkle=False):
    image = _blank()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([10, 6, 37, 20], radius=5, fill=_WOOD_DARK)
    for x in (14, 32):
        draw.rectangle([x, 6, x + 2, 20], fill=GOLD)
    draw.ellipse([11, 15, 36, 32], fill=_COIN)
    for x, y in [(15, 22), (20, 18), (26, 20), (31, 23), (23, 24), (17, 26), (29, 27)]:
        draw.rectangle([x, y, x + 2, y + 1], fill=_COIN_LIT)
    draw.rectangle([22, 19, 24, 21], fill=_RED)
    draw.rectangle([29, 19, 30, 20], fill="#3f9ad0")
    _chest_body(draw)
    draw.rectangle([21, 26, 26, 30], fill=GOLD)
    add_outline(image)
    stars = [(7, 8), (40, 13), (24, 3)] if sparkle else [(41, 6), (6, 16), (33, 2)]
    for x, y in stars:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            image.putpixel((x + dx, y + dy), rgba("#fffbe0"))
    return image


def mark_question():
    """A big gold question mark, on the square only the reader can see it on."""
    image = _blank()
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([14, 8, 33, 22], radius=6, fill=GOLD)
    draw.rectangle([20, 14, 27, 17], fill=(0, 0, 0, 0))
    draw.rectangle([14, 17, 22, 22], fill=(0, 0, 0, 0))
    draw.rectangle([21, 21, 27, 29], fill=GOLD)
    draw.rectangle([21, 33, 27, 39], fill=GOLD)
    add_outline(image)
    return image


def mark_x():
    """The X that marks the spot, painted red on the ground."""
    image = _blank()
    draw = ImageDraw.Draw(image)
    draw.line([(11, 11), (36, 36)], fill=_RED, width=6)
    draw.line([(36, 11), (11, 36)], fill=_RED, width=6)
    add_outline(image, "#6e1a1c")
    return image


ITEMS = {
    "treasure-closed": closed,
    "treasure-open": opened,
    "treasure-open-2": lambda: opened(True),
    "mark-question": mark_question,
    "mark-x": mark_x,
}
