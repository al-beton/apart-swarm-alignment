# Implements: assets/any-pirate, assets/charming-personalities, assets/label-on-hat, assets/four-directions, assets/actions-shown, assets/dig-motion, assets/viewer-parts, assets/original-art
"""Pirates: pirate(personality, colour, label, pose, frame) gives a 48x48 RGBA sprite.

The colour tints the hat and coat. The label, up to two letters or digits, sits in a
cream blob on the hat, so it reads the same on any colour. Walk by looping frames
0, 1, 0, 2 of a facing; dig and cheer have frames 0 and 1.
"""

import math
from dataclasses import dataclass
from itertools import pairwise

from PIL import Image, ImageDraw, ImageOps

from assets.pixels import (
    CREAM,
    DARK,
    GOLD,
    OUTLINE,
    SIZE,
    Pen,
    add_outline,
    hx,
    shade,
)

FACINGS = ("down", "up", "right", "left")
POSES = (*FACINGS, "dig", "cheer")

DEFAULT_COLOURS = (
    "#c8403c", "#2f6fc0", "#3f9a4e", "#e08a2c", "#8a4cc0",
    "#20a0a0", "#d84c90", "#7a8a30", "#b06c34", "#4858b8",
    "#e0b030", "#a03048", "#58a8e0", "#68b060", "#9c5ca0",
    "#e06a50", "#308068", "#808898", "#c0a060", "#5c4098",
)  # fmt: skip

_SKIN = {
    1: "#f4cfa8", 2: "#ecbc92", 3: "#dfa97e", 4: "#c8905f",
    5: "#a87448", 6: "#8c5c38", 7: "#6e462a",
}  # fmt: skip
_HAIR = {
    "black": "#2c2230", "brown": "#6e4030", "auburn": "#9a5030",
    "grey": "#a8a4a8", "blond": "#d8b050",
}  # fmt: skip

# Personality: skin, face, hair, extras.
PERSONALITIES = {
    1: (3, "beard", "brown", {"patch"}),
    2: (5, "clean", "black", {"earring"}),
    3: (1, "moustache", "auburn", set()),
    4: (6, "beard", "black", set()),
    5: (2, "long", "blond", {"grin"}),
    6: (7, "clean", "black", {"earring"}),
    7: (4, "long", "black", set()),
    8: (3, "beard", "grey", {"patch"}),
    9: (6, "moustache", "black", set()),
    10: (1, "beard", "auburn", set()),
    11: (3, "long", "brown", {"grin"}),
    12: (7, "beard", "black", {"earring"}),
    13: (2, "clean", "blond", set()),
    14: (4, "long", "brown", {"patch"}),
    15: (2, "moustache", "grey", set()),
    16: (5, "clean", "black", {"grin"}),
    17: (7, "long", "black", set()),
    18: (1, "beard", "brown", set()),
    19: (3, "clean", "auburn", {"earring"}),
    20: (5, "beard", "grey", {"patch"}),
}

# Blob characters, 3x5, drawn 2x2 so they are bold at game size.
_BLOB_GLYPHS = {
    "0": "### #.# #.# #.# ###", "1": ".#. ##. .#. .#. ###", "2": "### ..# ### #.. ###",
    "3": "### ..# .## ..# ###", "4": "#.# #.# ### ..# ..#", "5": "### #.. ### ..# ###",
    "6": "### #.. ### #.# ###", "7": "### ..# .#. .#. .#.", "8": "### #.# ### #.# ###",
    "9": "### #.# ### ..# ###", "A": "### #.# ### #.# #.#", "B": "##. #.# ##. #.# ##.",
    "C": "### #.. #.. #.. ###", "D": "##. #.# #.# #.# ##.", "E": "### #.. ##. #.. ###",
    "F": "### #.. ##. #.. #..", "G": "### #.. #.# #.# ###", "H": "#.# #.# ### #.# #.#",
    "I": "### .#. .#. .#. ###", "J": "..# ..# ..# #.# ###", "K": "#.# #.# ##. #.# #.#",
    "L": "#.. #.. #.. #.. ###", "M": "#.# ### ### #.# #.#", "N": "##. #.# #.# #.# #.#",
    "O": "### #.# #.# #.# ###", "P": "### #.# ### #.. #..", "Q": "### #.# #.# ### ..#",
    "R": "### #.# ##. #.# #.#", "S": "### #.. ### ..# ###", "T": "### .#. .#. .#. .#.",
    "U": "#.# #.# #.# #.# ###", "V": "#.# #.# #.# #.# .#.", "W": "#.# #.# ### ### #.#",
    "X": "#.# #.# .#. #.# #.#", "Y": "#.# #.# .#. .#. .#.", "Z": "### ..# .#. #.. ###",
}  # fmt: skip

_TROUSERS, _BOOT, _BOOT_LIT = "#4a4560", "#4a2c28", "#6e4a3c"
_BELT, _BUCKLE, _SHIRT, _EARRING = "#5a3a2a", "#e8c860", "#efe2c0", "#f0c840"
_WOOD = "#8a5a2b"


@dataclass(frozen=True)
class Look:
    coat: str
    coat_dark: str
    skin: str
    skin_dark: str
    hair: str
    face: str
    extras: frozenset


def _look(personality, colour):
    skin_key, face, hair_key, extras = PERSONALITIES[personality]
    skin = _SKIN[skin_key]
    return Look(
        colour,
        shade(colour, 0.72),
        skin,
        shade(skin, 0.82),
        _HAIR[hair_key],
        face,
        frozenset(extras),
    )


def _hat(pen, look, side=False):
    if side:
        top = [(5, 11), (10, 13), (13, 8), (15, 4), (20, 2), (28, 2)]
        top += [(32, 4), (34, 9), (38, 12), (44, 7)]
    else:
        top = [(3, 9), (8, 12), (12, 9), (14, 4), (19, 2), (28, 2)]
        top += [(33, 4), (35, 9), (39, 12), (44, 9)]
    pen.poly(top + [(43, 15), (37, 17), (10, 17), (5, 15)], look.coat)
    under = [
        (5, 15),
        (10, 17),
        (37, 17),
        (43, 15),
        (41, 14),
        (36, 15),
        (11, 15),
        (7, 14),
    ]
    pen.poly(under, look.coat_dark)
    for start, end in pairwise(top):
        pen.line(start, end, GOLD)
    pen.line((10, 18), (37, 18), OUTLINE)


def _front_legs(pen, frame):
    for x0, lift in ((16, 2 if frame == 2 else 0), (24, 2 if frame == 1 else 0)):
        pen.draw.rectangle([x0 + 1, 41, x0 + 6, 44 - lift], fill=_TROUSERS)
        pen.draw.rectangle([x0, 44 - lift, x0 + 7, 46 - lift], fill=_BOOT)
        pen.draw.rectangle([x0 + 1, 44 - lift, x0 + 6, 44 - lift], fill=_BOOT_LIT)


def _arm(pen, look, x0, drop=0):
    """A hanging arm, 4 wide, shaded on its outer side."""
    outer = x0 if x0 < 20 else x0 + 2
    pen.rect(x0, 31, x0 + 3, 37 + drop, look.coat)
    pen.rect(outer, 31, outer + 1, 37 + drop, look.coat_dark)
    pen.rect(x0, 37 + drop, x0 + 3, 37 + drop, CREAM)
    pen.rect(x0, 38 + drop, x0 + 3, 40 + drop, look.skin)


def _back_of_coat(pen, look):
    points = [
        (15, 29),
        (32, 29),
        (34, 31),
        (34, 39),
        (35, 42),
        (12, 42),
        (13, 39),
        (13, 31),
    ]
    pen.poly(points, look.coat)
    pen.line((13, 32), (13, 39), OUTLINE)
    pen.line((34, 32), (34, 39), OUTLINE)
    pen.rect(14, 36, 33, 38, _BELT)


def _front_coat(pen, look):
    _back_of_coat(pen, look)
    pen.poly([(19, 29), (28, 29), (24, 35), (23, 35)], _SHIRT)
    pen.line((19, 29), (23, 35), look.coat_dark)
    pen.line((28, 29), (24, 35), look.coat_dark)
    pen.rect(22, 36, 25, 38, _BUCKLE)
    for x0 in (15, 23, 31):
        pen.rect(x0, 39, x0 + 1, 42, look.coat_dark)


def _eyes(pen, look):
    brow = shade(look.hair, 0.8)
    if "patch" in look.extras:
        pen.rect(16, 19, 21, 23, DARK)
        pen.line((21, 19), (26, 17), DARK)
        pen.line((16, 20), (14, 22), DARK)
    else:
        pen.rect(17, 19, 20, 19, brow)
        pen.rect(18, 20, 19, 22, DARK)
        pen.dot(18, 20, "#ffffff")
    pen.rect(27, 19, 30, 19, brow)
    pen.rect(28, 20, 29, 22, DARK)
    pen.dot(28, 20, "#ffffff")
    pen.rect(23, 23, 24, 24, look.skin_dark)


def _front_mouth(pen, look):
    mouth = shade(look.skin, 0.55)
    if look.face == "beard":
        beard = [
            (14, 21),
            (17, 24),
            (30, 24),
            (33, 21),
            (33, 26),
            (28, 30),
            (19, 30),
            (14, 26),
        ]
        pen.poly(beard, look.hair)
        pen.rect(21, 26, 26, 26, mouth)
    elif look.face == "moustache":
        pen.rect(18, 24, 29, 25, look.hair)
        pen.rect(17, 26, 18, 26, look.hair)
        pen.rect(29, 26, 30, 26, look.hair)
    else:
        pen.rect(20, 26, 27, 26, mouth)
    if "grin" in look.extras:
        pen.rect(20, 25, 27, 27, CREAM)
        pen.line((20, 26), (27, 26), mouth)


def _front_head(pen, look):
    if look.face == "long":
        pen.rect(11, 16, 15, 34, look.hair)
        pen.rect(32, 16, 36, 34, look.hair)
    pen.oval(13, 12, 34, 29, look.skin)
    pen.rect(12, 20, 13, 23, look.skin)
    pen.rect(34, 20, 35, 23, look.skin)
    pen.rect(32, 18, 33, 24, look.skin_dark)
    pen.line((16, 29), (31, 29), OUTLINE)
    if look.face == "long":
        pen.rect(13, 16, 15, 26, look.hair)
        pen.rect(32, 16, 34, 26, look.hair)
    _eyes(pen, look)
    _front_mouth(pen, look)
    if "earring" in look.extras:
        pen.rect(35, 24, 36, 26, _EARRING)


def _front_body(pen, look):
    _front_coat(pen, look)
    _front_head(pen, look)
    _hat(pen, look)


def _draw_down(pen, look, frame):
    _front_legs(pen, frame)
    _arm(pen, look, 9, -1 if frame == 2 else 0)
    _arm(pen, look, 35, -1 if frame == 1 else 0)
    _front_body(pen, look)


def _draw_up(pen, look, frame):
    _front_legs(pen, frame)
    _arm(pen, look, 9, -1 if frame == 2 else 0)
    _arm(pen, look, 35, -1 if frame == 1 else 0)
    _back_of_coat(pen, look)
    pen.rect(23, 39, 24, 42, look.coat_dark)
    pen.rect(23, 30, 24, 35, look.coat_dark)
    pen.oval(13, 12, 34, 29, look.hair)
    pen.rect(12, 20, 13, 23, look.skin)
    pen.rect(34, 20, 35, 23, look.skin)
    pen.rect(19, 28, 28, 29, look.skin_dark)
    if look.face == "long":
        pen.rect(13, 16, 34, 35, look.hair)
        pen.rect(16, 28, 31, 35, shade(look.hair, 0.85))
    if "earring" in look.extras:
        pen.rect(35, 24, 36, 26, _EARRING)
    _hat(pen, look)


def _side_legs(pen, frame):
    far, near = {0: (21, 21), 1: (16, 26), 2: (26, 16)}[frame]
    for x0, dark in ((far, 0.75), (near, 1)):
        lift = 1 if frame and x0 < 21 else 0
        pen.draw.rectangle([x0, 41, x0 + 6, 44 - lift], fill=shade(_TROUSERS, dark))
        pen.draw.rectangle([x0, 44 - lift, x0 + 8, 46 - lift], fill=shade(_BOOT, dark))
        top = shade(_BOOT_LIT, dark)
        pen.draw.rectangle([x0 + 1, 44 - lift, x0 + 6, 44 - lift], fill=top)


def _side_coat(pen, look):
    points = [
        (18, 29),
        (30, 29),
        (31, 31),
        (31, 39),
        (33, 42),
        (15, 42),
        (16, 39),
        (17, 31),
    ]
    pen.poly(points, look.coat)
    pen.rect(27, 29, 30, 34, _SHIRT)
    pen.line((27, 29), (27, 34), look.coat_dark)
    pen.rect(17, 36, 30, 38, _BELT)
    pen.rect(27, 36, 29, 38, _BUCKLE)
    pen.rect(18, 39, 19, 42, look.coat_dark)


def _side_mouth(pen, look):
    mouth = shade(look.skin, 0.55)
    if look.face == "beard":
        beard = [(21, 24), (33, 24), (34, 26), (30, 30), (24, 30), (21, 27)]
        pen.poly(beard, look.hair)
        pen.rect(29, 26, 32, 26, mouth)
    elif look.face == "moustache":
        pen.rect(28, 24, 33, 25, look.hair)
        pen.rect(27, 26, 28, 26, look.hair)
    else:
        pen.rect(29, 26, 32, 26, mouth)
    if "grin" in look.extras:
        pen.rect(28, 25, 32, 27, CREAM)
        pen.line((28, 26), (32, 26), mouth)


def _side_head(pen, look):
    if look.face == "long":
        pen.rect(14, 16, 20, 34, look.hair)
    pen.oval(15, 12, 33, 29, look.skin)
    pen.rect(33, 22, 34, 24, look.skin)
    pen.rect(15, 15, 20, 27, look.hair)
    pen.oval(15, 14, 21, 26, look.hair)
    pen.rect(21, 20, 22, 23, look.skin_dark)
    pen.rect(26, 28, 30, 29, look.skin_dark)
    pen.line((19, 29), (29, 29), OUTLINE)
    pen.rect(27, 19, 30, 19, shade(look.hair, 0.8))
    pen.rect(28, 20, 29, 22, DARK)
    pen.dot(28, 20, "#ffffff")
    _side_mouth(pen, look)
    if "patch" in look.extras:
        pen.rect(26, 19, 31, 23, DARK)
        pen.line((26, 19), (20, 17), DARK)
    if "earring" in look.extras:
        pen.rect(21, 24, 22, 26, _EARRING)


def _side_arm(pen, look, frame):
    x0 = {0: 22, 1: 20, 2: 24}[frame]
    pen.rect(x0, 31, x0 + 4, 37, look.coat_dark)
    pen.rect(x0, 37, x0 + 4, 37, CREAM)
    pen.rect(x0, 38, x0 + 4, 40, look.skin)
    pen.line((x0 - 1, 32), (x0 - 1, 40), OUTLINE)
    pen.line((x0 + 5, 32), (x0 + 5, 40), OUTLINE)
    pen.line((x0, 41), (x0 + 4, 41), OUTLINE)


def _draw_right(pen, look, frame):
    _side_legs(pen, frame)
    _side_coat(pen, look)
    _side_head(pen, look)
    _side_arm(pen, look, frame)
    _hat(pen, look, side=True)


def _draw_cheer(pen, look, frame):
    _front_legs(pen, 0)
    for x0 in (6, 38):
        pen.rect(x0, 24, x0 + 3, 33, look.coat_dark)
        pen.rect(x0, 24, x0 + 3, 24, CREAM)
        pen.rect(x0, 20 - frame, x0 + 3, 23, look.skin)
    _front_body(pen, look)


# The dig is a pickaxe swing. The pirate steps left so the swing has the right of
# its square. Each stance: the hand on the haft, the haft's angle (0 points right,
# 90 up), the body's lift (up is negative) and the haft's length.
DIG_STANCES = (
    ((37, 25), 72, -2, 20),  # raised high: dig frame 0
    ((38, 27), 38, -1, 14),  # swinging down
    ((34, 33), -72, 2, 10),  # the point in the sand: dig frame 1
    ((34, 33), -72, 2, 10),  # held there while the chips fly
    ((37, 27), 55, 0, 16),  # lifting out
    ((37, 25), 72, -2, 20),  # raised again, as dig frame 0
)
_DIG_STEP_LEFT = 6
_IRON, _IRON_LIT = "#9aa4ae", "#d8e0e8"


def _pick_head(stance):
    """The haft's end and the two points of the pickaxe's curved head."""
    (hx_, hy), angle, lift, length = stance
    a = math.radians(angle)
    hy += lift
    end = (hx_ + length * math.cos(a), hy - length * math.sin(a))
    across = (-math.sin(a), -math.cos(a))
    along = (math.cos(a), -math.sin(a))
    head = []
    for t in range(-9, 10):
        bend = 2 - (t / 9) ** 2 * 4  # the points curve back toward the hand
        head.append(
            (
                end[0] + across[0] * t + along[0] * bend,
                end[1] + across[1] * t + along[1] * bend,
            )
        )
    return (hx_, hy), end, head


def pick_point(stance):
    """Where the pickaxe's lower point is in this stance, kept on the square."""
    _, _, head = _pick_head(DIG_STANCES[stance])
    x, y = max((head[0], head[-1]), key=lambda point: point[1])
    return min(round(x), SIZE - 4), min(round(y), SIZE - 3)


def _pickaxe(stance):
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    hand, end, head = _pick_head(stance)
    draw.line([hand, end], fill=_BOOT, width=3)
    draw.line([hand, end], fill=_WOOD, width=1)
    draw.line(head, fill=_IRON, width=3)
    draw.line(head[3:-3], fill=_IRON_LIT, width=1)
    add_outline(layer)
    return layer


def _swinging_arm(look, hand):
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pen = Pen(layer)
    shoulder = (31, 31)
    pen.line(shoulder, hand, look.coat_dark, width=5)
    pen.line(shoulder, hand, look.coat, width=3)
    pen.rect(hand[0] - 2, hand[1] - 2, hand[0] + 1, hand[1] + 1, look.skin)
    add_outline(layer)
    return layer


def swing(personality, colour, label, stance):
    """48x48: the pirate a stance into its pickaxe swing, 0 to len(DIG_STANCES) - 1.

    The dig pose's frames are stances 0 (raised) and 2 (struck).
    """
    if not 0 <= stance < len(DIG_STANCES):
        raise ValueError(f"stance must be 0 to {len(DIG_STANCES) - 1}: {stance}")
    look = _look(personality, colour)
    lift = DIG_STANCES[stance][2]
    body = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    pen = Pen(body, lift)
    _front_legs(pen, 0)
    _arm(pen, look, 9)
    _front_body(pen, look)
    add_outline(body)
    if label:
        _add_blob(body, label, 4 + lift)
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    image.alpha_composite(body.crop((_DIG_STEP_LEFT, 0, SIZE, SIZE)))
    hand, _, _ = _pick_head(DIG_STANCES[stance])
    image.alpha_composite(_pickaxe(DIG_STANCES[stance]))
    image.alpha_composite(_swinging_arm(look, hand))
    return image


_DRAW = {
    "down": _draw_down,
    "up": _draw_up,
    "right": _draw_right,
    "left": _draw_right,
    "cheer": _draw_cheer,
}


def _bob(pose, frame):
    if pose == "cheer":
        return -2 if frame == 1 else 0
    return -1 if frame else 0


def _add_blob(image, label, top):
    draw = ImageDraw.Draw(image)
    width = len(label) * 8 - 2
    x0 = 24 - width // 2
    box = [x0 - 3, top - 2, x0 + width + 2, top + 11]
    draw.rounded_rectangle(box, radius=3, fill=CREAM, outline=OUTLINE)
    ink = hx(DARK) + (255,)
    for i, char in enumerate(label):
        for y, row in enumerate(_BLOB_GLYPHS[char].split()):
            for x, bit in enumerate(row):
                if bit == "#":
                    x1, y1 = x0 + i * 8 + x * 2, top + y * 2
                    draw.rectangle([x1, y1, x1 + 1, y1 + 1], fill=ink)


def pirate(personality, colour, label="", pose="down", frame=0):
    """A 48x48 RGBA sprite. colour is "#rrggbb"; label is up to two letters or digits."""
    label = label.upper()
    if len(label) > 2 or any(char not in _BLOB_GLYPHS for char in label):
        raise ValueError(f"label must be up to 2 letters or digits: {label!r}")
    if pose == "dig":
        return swing(personality, colour, label, (0, 2)[frame])
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    dy = _bob(pose, frame)
    _DRAW[pose](Pen(image, dy), _look(personality, colour), frame)
    add_outline(image)
    if pose == "left":
        image = ImageOps.mirror(image)
    if label:
        _add_blob(image, label, 4 + dy)
    return image


def portrait(personality, colour, label=""):
    """The hat and head at twice the size, 96x64, for the side panel."""
    head = pirate(personality, colour, label).crop((0, 0, SIZE, 32))
    return head.resize((96, 64), Image.NEAREST)
