# Implements: assets/treasure-shown, assets/original-art
"""The marks on the treasure's square: 48x48 with a transparent background."""

from PIL import Image, ImageDraw

from assets.pixels import GOLD, SIZE, add_outline


def _blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


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


ITEMS = {
    "mark-question": mark_question,
}
