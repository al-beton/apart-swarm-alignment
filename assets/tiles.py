# Implements: assets/ground-tiles, assets/original-art
"""Ground tiles, 48x48 and opaque. Each is drawn from a fixed seed, so it never changes."""

import random

from PIL import Image, ImageDraw

from assets.pixels import SIZE, rgba

_SAND = "#d9c08c"
_SAND_MARKS = ("#c8ab74", "#c8ab74", "#e6d2a4")
_SAND_EDGE = "#cfb37e"


def _scatter(image, colours, count, seed):
    rng = random.Random(seed)
    pixels = image.load()
    for _ in range(count):
        pixels[rng.randrange(SIZE), rng.randrange(SIZE)] = rgba(rng.choice(colours))


def _edges(image):
    """A faint dotted edge, so a reader can count squares without a heavy grid."""
    pixels = image.load()
    for i in range(0, SIZE, 2):
        pixels[i, 0] = rgba(_SAND_EDGE)
        pixels[0, i] = rgba(_SAND_EDGE)


def sand(seed=11):
    image = Image.new("RGBA", (SIZE, SIZE), rgba(_SAND))
    _scatter(image, _SAND_MARKS, 150, seed)
    _edges(image)
    return image


def dug():
    """Turned-over sand: clods and a shallow scoop, clearly walkable, not a pit."""
    image = sand()
    rng = random.Random(23)
    pixels = image.load()
    for y in range(6, 42):
        for x in range(5, 43):
            inside = ((x - 24) / 18) ** 2 + ((y - 24) / 17) ** 2
            if inside + rng.uniform(-0.2, 0.2) < 1:
                pixels[x, y] = rgba(rng.choice(("#b8965f", "#a8854f", "#bf9f68")))
    draw = ImageDraw.Draw(image)
    draw.ellipse([16, 19, 32, 29], fill=rgba("#9a7a48"))
    draw.ellipse([18, 22, 30, 29], fill=rgba("#8c6e40"))
    for _ in range(11):
        x, y = rng.randrange(8, 37), rng.randrange(8, 37)
        if 16 <= x <= 30 and 17 <= y <= 28:
            continue
        draw.rectangle([x, y, x + 3, y + 1], fill=rgba("#d6bb84"))
        draw.rectangle([x, y + 2, x + 3, y + 2], fill=rgba("#8f7044"))
    return image


def water(frame=0):
    """The waves shift by 3px between frames 0 and 1."""
    image = Image.new("RGBA", (SIZE, SIZE), rgba("#3f8fc4"))
    _scatter(image, ("#3786bb", "#4a9ace"), 120, 5)
    pixels = image.load()
    crest, trough = rgba("#a4dcf0"), rgba("#2f78ae")
    rows = [(5, 6), (13, 30), (21, 14), (29, 38), (37, 3), (44, 24)]
    for y, x0 in rows:
        for i in range(7):
            x = (x0 + i + frame * 3) % SIZE
            lift = 1 if i in (2, 3, 4) else 0
            pixels[x, y - lift] = crest
            pixels[x, y - lift + 1] = trough
    return image


def sinking_sand():
    """Wet, swirling sand: looks as unsafe as it is once someone has found it."""
    image = Image.new("RGBA", (SIZE, SIZE), rgba("#b39660"))
    _scatter(image, ("#a68a55", "#bda26c"), 120, 31)
    draw = ImageDraw.Draw(image)
    rings = [(5, "#9c8150"), (10, "#b39660"), (14, "#8a7044"), (19, "#a68a55")]
    for inset, colour in rings:
        draw.ellipse(
            [inset, inset + 3, SIZE - 1 - inset, SIZE - 4 - inset], fill=rgba(colour)
        )
    draw.ellipse([20, 23, 27, 26], fill=rgba("#6e5832"))
    for x, y in [(10, 12), (36, 34), (35, 11)]:
        draw.rectangle([x, y, x + 1, y + 1], fill=rgba("#d6c08e"))
    return image


TILES = {
    "sand": sand,
    "sand-2": lambda: sand(12),
    "sand-3": lambda: sand(13),
    "dug": dug,
    "water": water,
    "water-2": lambda: water(1),
    "sinking-sand": sinking_sand,
}
