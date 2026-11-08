# Implements: assets/dig-motion, assets/original-art
"""A pirate digging, over six steps, for the turn it digs.

It swings a pickaxe: raised high, swung down, the point struck into the sand
with a burst, chips of sand flying, and lifted out again, while the dug ground
spreads from the middle of the square. The last step is the dig pose raised,
on dug sand.
"""

import math
import random

from PIL import Image, ImageDraw

from assets.pirates import DIG_STANCES, pick_point, swing
from assets.pixels import SIZE, add_outline
from assets.tiles import TILES

DIG_STEPS = len(DIG_STANCES)
_DIRT, _DIRT_DARK, _DIRT_LIT = "#9a7a48", "#7a5c34", "#c8a870"
_BURST = "#fff4c8"
_HOLE = (0, 0, 0.45, 0.7, 1.2, 0)  # how far the dug ground has spread
_BURSTS = {2: 1, 3: 2}  # step: the burst's size where the point strikes
_CHIPS = {3: 0, 4: 1}  # step: how long the chips have been flying
_CHIP_SPEEDS = ((-5, -6), (4, -8), (7, -4), (-8, -3), (1, -9))


def _step(step):
    if not 0 <= step < DIG_STEPS:
        raise ValueError(f"step must be 0 to {DIG_STEPS - 1}: {step}")


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


def _burst(image, at, size):
    draw = ImageDraw.Draw(image)
    x, y = at
    for i in range(8):
        angle = i * math.pi / 4
        near, far = 2 + size, 5 + size * 2
        start = (x + near * math.cos(angle), y + near * math.sin(angle) * 0.6)
        end = (x + far * math.cos(angle), y + far * math.sin(angle) * 0.6)
        draw.line([start, end], fill=_BURST)


def _chips(at, moment):
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = at
    for i, (vx, vy) in enumerate(_CHIP_SPEEDS):
        k = moment + 1
        cx, cy = x + vx * k, y + vy * k + 3 * k * k
        colour = (_DIRT, _DIRT_DARK, _DIRT_LIT)[i % 3]
        draw.rectangle([cx, cy, cx + 2, cy + 1], fill=colour)
    add_outline(layer)
    return layer


def digging(personality, colour, label, step):
    """48x48 over dig_ground(step): the pirate swinging its pickaxe, chips flying."""
    _step(step)
    image = swing(personality, colour, label, step)
    point = pick_point(step)
    if step in _CHIPS:
        image.alpha_composite(_chips(point, _CHIPS[step]))
    if step in _BURSTS:
        _burst(image, point, _BURSTS[step])
    return image
