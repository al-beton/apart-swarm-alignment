# Implements: assets/plain-files, assets/remade-by-one-command, assets/sheet-shows-everything
"""Draws every image in assets/ from code: `make assets` or `python -m assets.generate`."""

from pathlib import Path

from PIL import Image

from assets.font import FONT_HEIGHT, draw_text, font_sheet, text_width
from assets.pirates import DEFAULT_COLOURS, PERSONALITIES, pirate, portrait
from assets.pixels import DARK, SIZE
from assets.tiles import TILES, sand
from assets.treasure import ITEMS
from assets.ui import (
    bubble_slices,
    bubble_tail,
    panel,
    panel_slices,
    speech_bubble,
    turn_arrow,
)

ASSETS = Path(__file__).resolve().parent

# Rows of a pirate sprite sheet, each with its frames, left to right.
SHEET_ROWS = (
    ("down", 3),
    ("up", 3),
    ("right", 3),
    ("left", 3),
    ("dig", 2),
    ("cheer", 2),
)
_BACKGROUND = (250, 248, 243, 255)
_MUTED = "#78727a"


def pirate_sheet(number):
    """One crew member, labelled with its number, 144x288: columns are frames."""
    image = Image.new("RGBA", (3 * SIZE, len(SHEET_ROWS) * SIZE), (0, 0, 0, 0))
    colour = DEFAULT_COLOURS[number - 1]
    for row, (pose, frames) in enumerate(SHEET_ROWS):
        for frame in range(frames):
            sprite = pirate(number, colour, str(number), pose, frame)
            image.paste(sprite, (frame * SIZE, row * SIZE))
    return image


def _heading(sheet, y, text, note=""):
    big = Image.new("RGBA", (text_width(text), FONT_HEIGHT), (0, 0, 0, 0))
    draw_text(big, (0, 0), text, DARK)
    big = big.resize((big.width * 2, big.height * 2), Image.NEAREST)
    sheet.alpha_composite(big, (24, y))
    if note:
        draw_text(sheet, (32 + big.width, y + 6), note, _MUTED)


def _on_sand(items, columns):
    """Sprites in a grid on sand, as the reader sees them."""
    rows = (len(items) + columns - 1) // columns
    board = Image.new("RGBA", (columns * SIZE, rows * SIZE))
    tile = sand()
    for row in range(rows):
        for column in range(columns):
            board.paste(tile, (column * SIZE, row * SIZE))
    for i, sprite in enumerate(items):
        board.alpha_composite(sprite, (i % columns * SIZE, i // columns * SIZE))
    return board


def _crew():
    return [pirate(n, DEFAULT_COLOURS[n - 1], str(n)) for n in PERSONALITIES]


def _poses():
    return [
        pirate(1, DEFAULT_COLOURS[0], "7", pose, frame)
        for pose, frames in SHEET_ROWS
        for frame in range(frames)
    ]


def _labelled_row(sheet, y, items):
    """Named images side by side, at twice real size so the detail shows."""
    x = 24
    for name, image in items:
        big = image.resize((image.width * 2, image.height * 2), Image.NEAREST)
        sheet.alpha_composite(big, (x, y))
        draw_text(sheet, (x, y + big.height + 4), name, _MUTED)
        x += max(big.width, len(name) * 6) + 12


def _place(scene, sprite, cell, offset=(0, 0)):
    scene.alpha_composite(
        sprite, (cell[0] * SIZE + offset[0], cell[1] * SIZE + offset[1])
    )


def _scene():
    """A little of the game, to judge everything together."""
    columns, rows = 8, 6
    scene = Image.new("RGBA", (columns * SIZE, rows * SIZE))
    for y in range(rows):
        for x in range(columns):
            name = "water" if x == 7 or (x == 6 and y < 2) else "sand"
            scene.paste(TILES[name](), (x * SIZE, y * SIZE))
    for cell in [(1, 1), (2, 1), (3, 1), (1, 2), (4, 3)]:
        scene.paste(TILES["dug"](), (cell[0] * SIZE, cell[1] * SIZE))
    scene.paste(TILES["sinking-sand"](), (5 * SIZE, 1 * SIZE))
    scene.paste(TILES["dug"](), (5 * SIZE, 4 * SIZE))
    _place(scene, ITEMS["mark-x"](), (5, 4))
    _place(scene, ITEMS["treasure-open"](), (5, 4))
    _place(scene, ITEMS["mark-question"](), (0, 5))
    crew = [
        ((2, 3), 1, "right", 1),
        ((3, 4), 2, "down", 0),
        ((1, 4), 3, "dig", 1),
        ((4, 4), 4, "cheer", 1),
        ((5, 3), 5, "down", 0),
        ((6, 4), 6, "left", 2),
    ]
    for cell, number, pose, frame in crew:
        sprite = pirate(number, DEFAULT_COLOURS[number - 1], str(number), pose, frame)
        _place(scene, sprite, cell)
    _place(scene, turn_arrow(), (2, 3), (16, -14))
    bubble = speech_bubble("I'll search row 1, the rest of you take row 2.")
    scene.alpha_composite(bubble, (2 * SIZE + 18, 3 * SIZE - 14 - bubble.height))
    return scene


def _side_panel():
    frame = panel(200, 288)
    frame.alpha_composite(portrait(1, DEFAULT_COLOURS[0], "1"), (52, 14))
    lines = [
        "Pirate 1's turn",
        "",
        "Row 1 is empty so",
        "far. Try the next",
        "square east.",
        "",
    ]
    lines += ["> move east"]
    for i, line in enumerate(lines):
        draw_text(frame, (16, 86 + i * 10), line)
    return frame


def _log():
    frame = panel(592, 64)
    lines = ["1: Let's split up. I'll take row 1.", "2: Sure, row 2 is mine."]
    lines += ["3: Row 3. Check in every 10 turns."]
    for i, line in enumerate(lines):
        draw_text(frame, (14, 12 + i * 12), line)
    return frame


def contact_sheet():
    """All the art on one page, to judge it at a glance."""
    sheet = Image.new("RGBA", (1024, 956), _BACKGROUND)
    _heading(
        sheet, 18, "The crew", "20 personalities, any colour, 48px squares at real size"
    )
    sheet.alpha_composite(_on_sand(_crew(), 10), (24, 46))
    _heading(sheet, 158, "One pirate", "walking in 4 directions, digging, cheering")
    sheet.alpha_composite(_on_sand(_poses(), 16), (24, 186))
    _heading(sheet, 250, "Ground", "enlarged 2x")
    _labelled_row(sheet, 278, [(name, make()) for name, make in TILES.items()])
    _heading(sheet, 398, "Treasure", "enlarged 2x, on no background")
    _labelled_row(sheet, 426, [(name, make()) for name, make in ITEMS.items()])
    _heading(sheet, 546, "In play", "the viewer parts together, at real size")
    sheet.alpha_composite(_scene(), (24, 574))
    sheet.alpha_composite(_side_panel(), (416, 574))
    sheet.alpha_composite(_log(), (24, 870))
    _parts(sheet)
    return sheet


def _parts(sheet):
    """The viewer's raw parts, beside the scene they build."""
    font = font_sheet()
    draw_text(sheet, (632, 574), "font", _MUTED)
    sheet.alpha_composite(
        font.resize((font.width * 2, font.height * 2), Image.NEAREST), (632, 586)
    )
    x, y = 632, 586 + font.height * 2 + 16
    for name, image in (
        ("arrow", turn_arrow()),
        ("tail", bubble_tail()),
        ("bubble", bubble_slices()),
        ("panel", panel_slices()),
    ):
        big = image.resize((image.width * 2, image.height * 2), Image.NEAREST)
        draw_text(sheet, (x, y), name, _MUTED)
        sheet.alpha_composite(big, (x, y + 12))
        x += max(big.width, len(name) * 6) + 16


def build():
    """Every committed image, by its path under assets/."""
    images = {f"pirates/pirate-{n:02}.png": pirate_sheet(n) for n in PERSONALITIES}
    images |= {f"tiles/{name}.png": make() for name, make in TILES.items()}
    images |= {f"treasure/{name}.png": make() for name, make in ITEMS.items()}
    images |= {
        "ui/font.png": font_sheet(),
        "ui/turn-arrow.png": turn_arrow(),
        "ui/bubble.png": bubble_slices(),
        "ui/bubble-tail.png": bubble_tail(),
        "ui/panel.png": panel_slices(),
        "sheet.png": contact_sheet(),
    }
    return images


def main():
    for name, image in build().items():
        path = ASSETS / name
        path.parent.mkdir(exist_ok=True)
        image.save(path, optimize=True)


if __name__ == "__main__":
    main()
