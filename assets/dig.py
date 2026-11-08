# Implements: assets/dig-motion, assets/original-art
"""A pirate digging, over six steps, for the turn it digs.

It raises the shovel, drives it in with a puff of dust, heaves, and the sand
arcs over its shoulder and lands beside the hole, which spreads from the middle
of the square. The last step is the plain dig pose on the dug tile, the same as
the turn's still frame.
"""

import math
import random

from PIL import Image, ImageDraw

from assets.pirates import pirate
from assets.pixels import SIZE, add_outline
from assets.tiles import TILES

DIG_STEPS = 6
_DIRT, _DIRT_DARK, _DIRT_LIT = "#9a7a48", "#7a5c34", "#c8a870"
_DUST = "#efe0b8"
_CLEAR = (0, 0, 0, 0)

# Each step: the dig frame, how far the pirate is lifted (up is negative), the
# sand's moment in the air (0 to 2) or None, the dust ring's size or None, and
# whether the sand has landed.
_STEPS = (
    (0, -3, None, None, False),  # shovel raised
    (1, 1, None, 0, False),  # driven in
    (0, -1, 0, 1, False),  # heave
    (0, -2, 1, None, False),  # over the shoulder
    (0, 0, 2, None, True),  # landing
    (0, 0, None, None, False),  # done: the still dig pose
)
_HOLE = (0, 0, 0.45, 0.7, 1.2, 0)  # how far the dug ground has spread
_BLADE = (38, 40)
# Where each clod lands, its shade, its size.
_CLODS = (
    ((6, 39), 0, 3),
    ((9, 41), 1, 3),
    ((4, 41), 2, 2),
    ((11, 38), 1, 2),
    ((7, 37), 0, 3),
    ((12, 42), 2, 2),
)


def _step(step):
    if not 0 <= step < DIG_STEPS:
        raise ValueError(f"step must be 0 to {DIG_STEPS - 1}: {step}")
    return _STEPS[step]


def dig_ground(step, ground=None):
    """48x48, opaque: the square's ground at this step, turning to dug sand.

    ground is the tile the square had before, plain sand if not given.
    """
    _step(step)
    ground = (TILES["sand"]() if ground is None else ground).copy()
    dug = TILES["dug"]()
    if step == DIG_STEPS - 1:
        return dug
    mask = Image.new("L", (SIZE, SIZE), 0)
    rng = random.Random(5)
    for y in range(SIZE):
        for x in range(SIZE):
            reach = math.hypot((x - 24) / 19, (y - 26) / 18) + rng.uniform(-0.08, 0.08)
            if _HOLE[step] and reach < _HOLE[step]:
                mask.putpixel((x, y), 255)
    ground.paste(dug, (0, 0), mask)
    return ground


def _clods(moment):
    layer = Image.new("RGBA", (SIZE, SIZE), _CLEAR)
    draw = ImageDraw.Draw(layer)
    (sx, sy), colours = _BLADE, (_DIRT, _DIRT_DARK, _DIRT_LIT)
    for i, ((lx, ly), shade, size) in enumerate(_CLODS):
        part = (0.18, 0.55, 0.88)[moment] + (i % 3 - 1) * 0.05
        height = (30 + i % 3 * 4) * math.sin(math.pi * part)
        x = round(sx + (lx - sx) * part)
        y = round(sy + (ly - sy) * part - height)
        draw.rectangle([x, y, x + size - 1, y + size - 2], fill=colours[shade])
    add_outline(layer)
    return layer


def _dust(image, size):
    draw = ImageDraw.Draw(image)
    for i in range(6):
        angle, reach = i * math.pi / 3, 4 + size * 3
        x = _BLADE[0] + int(reach * math.cos(angle))
        y = _BLADE[1] + 4 + int(reach * math.sin(angle) / 2)
        draw.point((x, y), fill=_DUST)


def _heap(image):
    draw = ImageDraw.Draw(image)
    draw.ellipse([3, 38, 13, 44], fill=_DIRT_DARK)
    draw.ellipse([4, 37, 12, 42], fill=_DIRT)
    draw.point((7, 38), fill=_DIRT_LIT)


def digging(personality, colour, label, step):
    """48x48 over dig_ground(step): the pirate and its shovel, with the sand in the air."""
    frame, lift, moment, dust, landed = _step(step)
    image = Image.new("RGBA", (SIZE, SIZE), _CLEAR)
    if landed:
        _heap(image)
    sprite = pirate(personality, colour, label, "dig", frame)
    above, below = max(-lift, 0), max(lift, 0)
    image.alpha_composite(sprite.crop((0, above, SIZE, SIZE - below)), (0, below))
    if moment is not None:
        image.alpha_composite(_clods(moment))
    if dust is not None:
        _dust(image, dust)
    return image
