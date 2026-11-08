# Implements: assets/treasure-cave, assets/hat-stack, assets/going-in, assets/enter-motion, assets/original-art
"""The treasure cave, the hats piled by its door, and a pirate going in.

Once the treasure is dug up its square becomes a cave, and a pirate that reaches
it goes inside rather than crowding the square. It leaves a small copy of its
hat on a stack by the entrance, so the square shows who has gone in, and in what
order, first at the bottom.
"""

import math
from itertools import pairwise

from PIL import Image, ImageDraw

from assets.pirates import _BLOB_GLYPHS, pirate
from assets.pixels import CREAM, DARK, GOLD, SIZE, add_outline, shade

_ROCK, _ROCK_DARK, _ROCK_LIT = "#a08872", "#7e6656", "#c0a88c"
_INSIDE, _WALL = "#2a1a28", "#4a2a24"
_COIN, _COIN_LIT = "#f0c840", "#fff0a0"
_CLEAR = (0, 0, 0, 0)
_GROUND = 44  # the cave's foot; below it the tile underneath shows

# The pirate's hat at about 2/5 size, same tricorn and gold trim, with a deep
# band under the brim for the label.
HAT_SIZE = (21, 13)
_HAT_TOP = [(2, 5), (4, 6), (6, 4), (7, 2), (9, 1), (13, 1), (15, 2), (16, 4)]
_HAT_TOP += [(18, 6), (20, 5)]
_LABEL_TOP = 6
STACK_STEP = HAT_SIZE[1] - _LABEL_TOP  # each hat leaves its label showing
STACK_ROOM = 6  # hats that fit on the square with every label showing
_STACK_X = SIZE - HAT_SIZE[0] - 1  # odd hats lean one pixel right
GOING_IN_STEPS = 4
_SINK = (0, 4, 9, 14)


def cave(frame=0):
    """48x48 on a transparent background: a rocky mound, gold glinting in its mouth.

    It sits left of centre to leave room for the hat stack. Alternate frames 0
    and 1 to make the gold glint.
    """
    image = Image.new("RGBA", (SIZE, SIZE), _CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse([1, 12, 36, 52], fill=_ROCK)
    draw.ellipse([3, 12, 31, 38], fill=_ROCK_LIT)
    draw.ellipse([5, 16, 36, 50], fill=_ROCK)
    for x, y in [(6, 30), (30, 24), (10, 21), (29, 36)]:
        draw.rectangle([x, y, x + 3, y + 1], fill=_ROCK_DARK)
    draw.rounded_rectangle([10, 24, 28, 46], radius=8, fill=_INSIDE)
    draw.ellipse([12, 28, 26, 42], fill=_WALL)
    draw.ellipse([12, 37, 26, 47], fill=_COIN)
    draw.rectangle([0, _GROUND, SIZE, SIZE], fill=_CLEAR)
    add_outline(image)
    specks = [(14, 40), (19, 38), (23, 41)] if frame == 0 else [(16, 39), (22, 39)]
    specks += [] if frame == 0 else [(18, 42)]
    for x, y in specks:
        draw.rectangle([x, y, x + 1, y], fill=_COIN_LIT)
    for x, y in [(7, 43), (29, 43)]:
        draw.ellipse([x, y, x + 3, y + 2], fill=_COIN)
        draw.point((x + 1, y), fill=_COIN_LIT)
    return image


def _hat_label(draw, label):
    width = len(label) * 4 - 1
    x0 = HAT_SIZE[0] // 2 - width // 2
    draw.rectangle([x0 - 1, _LABEL_TOP, x0 + width, _LABEL_TOP + 6], fill=CREAM)
    for i, char in enumerate(label):
        for y, row in enumerate(_BLOB_GLYPHS[char].split()):
            for x, bit in enumerate(row):
                if bit == "#":
                    draw.point((x0 + i * 4 + x, _LABEL_TOP + 1 + y), fill=DARK)


def mini_hat(colour, label=""):
    """21x13: a pirate's hat, small, in its colour, its label low in a cream blob."""
    label = label.upper()
    if len(label) > 2 or any(char not in _BLOB_GLYPHS for char in label):
        raise ValueError(f"label must be up to 2 letters or digits: {label!r}")
    image = Image.new("RGBA", HAT_SIZE, _CLEAR)
    draw = ImageDraw.Draw(image)
    draw.polygon(_HAT_TOP + [(20, 7), (18, 11), (3, 11), (1, 7)], fill=colour)
    draw.line([(3, 11), (18, 11)], fill=shade(colour, 0.72))
    for start, end in pairwise(_HAT_TOP):
        draw.line([start, end], fill=GOLD)
    add_outline(image)
    if label:
        _hat_label(draw, label)
    return image


def hat_stack(hats):
    """48x48 overlay for the cave square: one small hat per pirate inside.

    hats is a list of (colour, label) in the order the pirates went in; the first
    is at the bottom. Up to six show every label; a bigger crew squeezes up so
    the stack stays on the square.
    """
    image = Image.new("RGBA", (SIZE, SIZE), _CLEAR)
    for i, (colour, label) in enumerate(hats):
        image.alpha_composite(mini_hat(colour, label), hat_place(i, len(hats)))
    return image


def hat_place(index, count):
    """Where hat `index` of `count` sits on the square: its top-left (x, y)."""
    bottom = SIZE - HAT_SIZE[1]
    step = STACK_STEP if count <= STACK_ROOM else bottom // (count - 1)
    return _STACK_X + index % 2, bottom - index * step


def going_in(personality, colour, label, step):
    """48x48: the pirate from behind, sinking into the cave's mouth, steps 0 to 3.

    Draw it over the cave square. For a game's GIF, with one frame per turn, step
    1 alone reads as going in.
    """
    if not 0 <= step < GOING_IN_STEPS:
        raise ValueError(f"step must be 0 to {GOING_IN_STEPS - 1}: {step}")
    sprite = pirate(personality, colour, label, "up", step % 3)
    sink = _SINK[step]
    image = Image.new("RGBA", (SIZE, SIZE), _CLEAR)
    image.alpha_composite(sprite.crop((0, 0, SIZE, SIZE - sink)), (-6, sink))
    if step:  # the gold heap in the mouth hides its legs
        ImageDraw.Draw(image).rectangle([0, 40 - sink // 3, SIZE, SIZE], fill=_CLEAR)
    return image


ENTER_STEPS = 9
_HAT_FLIGHT = (0.3, 0.65, 1.0)  # how far along its arc the hat is, steps 4 to 6
_HAT_FROM = (12, 28)  # the cave's mouth


def _sparkle(draw, x, y, arms):
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))[: 1 + arms * 2]:
        draw.point((x + dx, y + dy), fill="#fffbe0")


def entering(personality, colour, label, hats, step):
    """48x48 over tiles/dug.png: the cave square on the turn this pirate goes in.

    hats are those already inside, as for hat_stack. Steps 0 to 3 it sinks into
    the mouth (going_in); 4 to 6 its hat flies out in an arc onto the top of the
    stack; at 7 the hat lands with a sparkle; 8 is the square as the next turn
    draws it, with the new hat on the stack.
    """
    if not 0 <= step < ENTER_STEPS:
        raise ValueError(f"step must be 0 to {ENTER_STEPS - 1}: {step}")
    after = [*hats, (colour, label)]
    image = cave(step // 2 % 2)
    image.alpha_composite(hat_stack(after if step >= len(_HAT_FLIGHT) + 4 else hats))
    if step < GOING_IN_STEPS:
        image.alpha_composite(going_in(personality, colour, label, step))
        return image
    x, y = hat_place(len(hats), len(after))
    if step < GOING_IN_STEPS + len(_HAT_FLIGHT) - 1:
        part = _HAT_FLIGHT[step - GOING_IN_STEPS]
        fx = _HAT_FROM[0] + (x - _HAT_FROM[0]) * part
        fy = _HAT_FROM[1] + (y - _HAT_FROM[1]) * part - 14 * math.sin(math.pi * part)
        image.alpha_composite(mini_hat(colour, label), (round(fx), round(fy)))
    elif step == GOING_IN_STEPS + len(_HAT_FLIGHT) - 1:
        image.alpha_composite(mini_hat(colour, label), (x, y))
    if step == ENTER_STEPS - 2:  # just landed
        draw = ImageDraw.Draw(image)
        _sparkle(draw, x - 2, y + 2, 2)
        _sparkle(draw, x + HAT_SIZE[0] - 1, y + 4, 1)
        _sparkle(draw, x + 10, max(y - 3, 1), 2)
    return image
