"""Turns a pirate's config into what the art takes: `pirate(*sprite_values(p))`.

The config lets head text be free-form, while the hat holds two letters or
digits, so this is the one place that decides what it shows. It needs nothing
from the art itself, so the game can load it without any drawing library.

Implements: treasure-island/any-config-draws, treasure-island/head-text-label, assets/label-on-hat
"""

import string

_LABEL_CHARACTERS = frozenset(string.ascii_uppercase + string.digits)
_LABEL_LENGTH = 2


def label_for(head_text):
    """The first two letters or digits of the head text, uppercased."""
    usable = [c for c in head_text.upper() if c in _LABEL_CHARACTERS]
    return "".join(usable[:_LABEL_LENGTH])


def sprite_values(pirate):
    """A pirate's config as `pirate()` in the art takes it: (personality, colour, label)."""
    red, green, blue = pirate.colour
    colour = f"#{red:02x}{green:02x}{blue:02x}"
    return pirate.personality, colour, label_for(pirate.head_text)
