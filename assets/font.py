# Implements: assets/viewer-parts, assets/original-art
"""A 5x7 pixel font for printable ASCII, for speech bubbles, the side panel and the log."""

from PIL import Image

from assets.pixels import DARK, rgba

FONT_WIDTH = 6  # 5 pixels and a gap
FONT_HEIGHT = 10  # 7 pixels, 2 for descenders and no extra gap
COLUMNS = 16

# One line per 16 characters from space, each character 7 rows of 5 bits as hex.
_ROWS = """
00000000000000 04040404040004 0a0a0000000000 0a0a1f0a1f0a0a 040f140e051e04 18190204081303 0c121408151 20d 04040000000000 02040808080402 08040202020408 000a041f040a00 0004041f040400 00000000040408 0000001f000000 00000000000c0c 01010204081010
0e111315191 10e 040c040404040e 0e11010204081f 1f02040201110e 02060a121f0202 1f101e0101110e 0608101e11110e 1f010204080808 0e11110e11110e 0e11110f01020c 000c0c000c0c00 000c0c000c0408 02040810080402 00001f001f0000 08040201020408 0e110102040004
0e11010d15150e 0e1111111f1111 1e11111e11111e 0e11101010110e 1c121111111 21c 1f10101e10101f 1f10101e101010 0e111017111 10f 1111111f111111 0e04040404040e 0702020202120c 11121418141211 1010101010101f 111b1515111111 11111915131111 0e11111111110e
1e11111e101010 0e11111115120d 1e11111e141211 0f10100e01011e 1f040404040404 1111111111110e 11111111110a04 1111111515150a 11110a040a1111 1111110a040404 1f01020408101f 0e08080808080e 10100804020101 0e02020202020e 040a1100000000 0000000000001f
08040000000000 00000e010f110f 10101619111 11e 00000e1010110e 01010d1311110f 00000e111f100e 0609081c080808 00000f110f010e 10101619111111 04000c0404040e 02000602021 20c 10101214181412 0c04040404040e 00001a15151111 00001619111111 00000e1111110e
00001e111e1010 00000d130f0101 00001619101010 00000e100e011e 08081c08080906 0000111111130d 00001111110a04 0000111115150a 0000110a040a11 00001111 0f010e 00001f0204081f 02040408040402 04040404040404 08040402040408 00000815020000
"""
_HEX = "".join(_ROWS.split())
CHARS = "".join(chr(c) for c in range(32, 127))
_GLYPHS = {ch: _HEX[i * 14 : (i + 1) * 14] for i, ch in enumerate(CHARS)}
# These sit 2 rows lower, so their tails hang below the line.
_DESCENDERS = {
    "g": "0f1111110f010e",
    "p": "1e1111111e1010",
    "q": "0f1111110f0101",
    "y": "111111110f010e",
}
_GLYPHS |= _DESCENDERS


def _rows(char):
    glyph = _GLYPHS.get(char, _GLYPHS["?"])
    return [int(glyph[i : i + 2], 16) for i in range(0, 14, 2)]


def text_width(text):
    return len(text) * FONT_WIDTH


def draw_text(image, position, text, colour=DARK):
    """Draws one line of text with its top left corner at position."""
    ink = rgba(colour)
    x0, y0 = position
    for i, char in enumerate(text):
        for y, bits in enumerate(_rows(char)):
            for x in range(5):
                drop = 2 if char in _DESCENDERS else 0
                px, py = x0 + i * FONT_WIDTH + x, y0 + y + drop
                inside = 0 <= px < image.width and 0 <= py < image.height
                if bits >> (4 - x) & 1 and inside:
                    image.putpixel((px, py), ink)


def wrap(text, columns):
    """Splits text into lines of at most columns characters, breaking long words."""
    lines, line = [], ""
    for word in text.split():
        while len(word) > columns:
            if line:
                lines.append(line)
                line = ""
            lines.append(word[:columns])
            word = word[columns:]
        if len(line) + len(word) + (1 if line else 0) > columns:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    return lines or [""]


def font_sheet():
    """Every character in a grid of FONT_WIDTH x FONT_HEIGHT cells, COLUMNS across."""
    rows = (len(CHARS) + COLUMNS - 1) // COLUMNS
    image = Image.new("RGBA", (COLUMNS * FONT_WIDTH, rows * FONT_HEIGHT), (0, 0, 0, 0))
    for i, char in enumerate(CHARS):
        column, row = i % COLUMNS, i // COLUMNS
        draw_text(image, (column * FONT_WIDTH, row * FONT_HEIGHT), char)
    return image
