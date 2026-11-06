# Implements: assets/game-size, assets/original-art
"""What all the art shares: the square size, colour helpers, outlines and a pen."""

from PIL import ImageDraw

SIZE = 48
OUTLINE = "#3a2230"
CREAM = "#fff4d6"
DARK = "#2a1a28"
GOLD = "#d8a840"


def hx(colour):
    """A colour written #rrggbb as an (r, g, b) tuple."""
    return tuple(int(colour[i : i + 2], 16) for i in (1, 3, 5))


def rgba(colour):
    return hx(colour) + (255,)


def to_hex(rgb):
    return "#" + "".join(f"{c:02x}" for c in rgb)


def shade(colour, factor):
    return to_hex(min(255, int(c * factor)) for c in hx(colour))


def lighten(colour, factor):
    return to_hex(int(c + (255 - c) * factor) for c in hx(colour))


def add_outline(image, colour=OUTLINE):
    """Draws a 1px outline in the transparent pixels touching the shape."""
    pixels = image.load()
    width, height = image.size
    ink = rgba(colour)

    def touches(x, y):
        neighbours = ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
        return any(
            0 <= nx < width and 0 <= ny < height and pixels[nx, ny][3] > 0
            for nx, ny in neighbours
        )

    edge = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if pixels[x, y][3] == 0 and touches(x, y)
    ]
    for point in edge:
        pixels[point] = ink


class Pen:
    """Drawing helpers that shift everything by dy, for a body that bobs on a step."""

    def __init__(self, image, dy=0):
        self.image, self.dy = image, dy
        self.draw = ImageDraw.Draw(image)

    def rect(self, x0, y0, x1, y1, colour):
        self.draw.rectangle([x0, y0 + self.dy, x1, y1 + self.dy], fill=colour)

    def line(self, start, end, colour, width=1):
        points = [(start[0], start[1] + self.dy), (end[0], end[1] + self.dy)]
        self.draw.line(points, fill=colour, width=width)

    def poly(self, points, colour):
        self.draw.polygon([(x, y + self.dy) for x, y in points], fill=colour)

    def oval(self, x0, y0, x1, y1, colour):
        self.draw.ellipse([x0, y0 + self.dy, x1, y1 + self.dy], fill=colour)

    def dot(self, x, y, colour):
        self.image.putpixel((x, y + self.dy), rgba(colour))
