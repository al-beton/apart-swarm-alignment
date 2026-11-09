# Implements: treasure-island/paper-figures, viewer/frame-headings
"""The paper's teaser: two of the viewer's frames from a committed game, side by side.

The left panel is the turn a pirate reads a leak: the leaked line is written in a
banner above the board, with an arrow from it to the treasure's square. The right
panel is the turn it writes that square on the scroll, with its line on the scroll
highlighted. Both are `viewer.frame`, so the teaser shows exactly what the replay does.
It reads only the run folder, so it needs no keys and no network.

Usage: python -m paper.teaser RUN LEAK_TURN PASS_TURN [OUT]
"""

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from assets.font import draw_text, text_width, wrap
from assets.ui import panel
from treasure_island import viewer
from treasure_island.squares import square_name

OUT = "paper/figures/teaser.png"
BANNER = 24 + 3 * viewer.LINE  # a parchment banner above each frame: a title, two rows
ARROW = (224, 60, 49)  # the arrow's red (default, Al to confirm)
HIGHLIGHT = (255, 210, 63)  # the highlighted scroll line's gold, the score's ink
GAP = 16  # dark space between the two panels
_LEAK = re.compile(r"\[[^\]]*\]")  # a leak rides in brackets after the reply's sentence


def _game(folder):
    records = viewer.records_in(folder)
    return records, viewer.grid_size(folder, records)


def _frame(folder, turn):
    records, size = _game(folder)
    return viewer.frame(
        records,
        turn,
        size,
        viewer.pirates_in(folder, records),
        viewer.treasure_in(folder, records),
        scoring=viewer.scoring_in(folder),
    )


def leak_line(record):
    """What leaked in this turn's reply: its bracketed part, else the whole reply."""
    result = str(record.get("result", ""))
    found = _LEAK.search(result)
    return found[0] if found else result


def _banner(width, lines):
    image = panel(width, BANNER)
    for row, text in enumerate(lines):
        draw = viewer.draw_bold if row == 0 else draw_text  # the turn heading is bold
        draw(image, (14, 12 + row * viewer.LINE), text)
    return image


def _with_banner(frame, lines):
    image = Image.new("RGB", (frame.width, BANNER + frame.height), "#2b2b2b")
    banner = _banner(frame.width, lines)
    image.paste(banner, (0, 0), banner)
    image.paste(frame, (0, BANNER))
    return image


def _arrow(image, start, end, width=3):
    """A straight arrow from `start` to `end`, its head on `end`."""
    draw = ImageDraw.Draw(image)
    draw.line([start, end], fill=ARROW, width=width)
    (x0, y0), (x1, y1) = start, end
    length = max(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5, 1)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    head = 10
    back = (x1 - ux * head, y1 - uy * head)
    draw.polygon(
        [
            end,
            (back[0] - uy * head / 2, back[1] + ux * head / 2),
            (back[0] + uy * head / 2, back[1] - ux * head / 2),
        ],
        fill=ARROW,
    )


def leak_panel(folder, turn):
    """The turn a pirate reads the leak, with an arrow from the line to the square."""
    records, size = _game(folder)
    record = records[turn]
    frame = _frame(folder, turn)
    line = leak_line(record)
    title = f"Turn {record['turn']}: {record['agent']} is told"
    rows = wrap(line, (frame.width - 28) // text_width("x"))[:2]
    image = _with_banner(frame, [title, *rows])
    x, y = viewer.treasure_in(folder, records)
    target = (
        viewer.EDGE_LEFT + x * viewer.TILE + viewer.TILE // 2,
        BANNER + y * viewer.TILE + viewer.TILE // 2,
    )
    name = square_name((x, y), size)
    at = rows[0].find(name) if rows else -1  # start the arrow under the square's name
    left = 14 + (max(at, 0)) * text_width("x") + text_width(name) // 2
    _arrow(image, (left, 12 + 2 * viewer.LINE), target)
    return image


def written_rows(folder, turn):
    """Which of the scroll strip's rows hold the line this turn wrote."""
    records, size = _game(folder)
    width = viewer.EDGE_LEFT + max(size, 1) * viewer.TILE + viewer.PANEL
    columns = (width - 2 * 14) // text_width("x")
    scoring = viewer.scoring_in(folder)
    lines = viewer._log_so_far(records, turn, scoring.first_line)
    mine = {number for number, _ in viewer._log_so_far([records[turn]], 0, 1)}
    newest = len(lines)
    tagged = []
    for at, (number, text) in enumerate(lines[-viewer.STRIP_ROWS :]):
        index = newest - min(newest, viewer.STRIP_ROWS) + at
        tagged += [index] * len(wrap(f"{number} {text}".rstrip(), columns))
    tagged = tagged[-viewer.STRIP_ROWS :]
    last = newest - 1 if mine and lines else None
    return [row for row, index in enumerate(tagged, start=1) if index == last]


def pass_panel(folder, turn, highlight=True):
    """The turn the pirate writes the square on the scroll, its line highlighted."""
    records, _ = _game(folder)
    record = records[turn]
    frame = _frame(folder, turn)
    title = f"Turn {record['turn']}: {record['agent']} writes on the scroll"
    image = _with_banner(frame, [title, "and doesn't say the leak led it there"])
    if highlight:
        draw = ImageDraw.Draw(image)
        top = image.height - viewer.STRIP
        for row in written_rows(folder, turn):
            y = top + 14 + row * viewer.LINE
            box = (10, y - 3, image.width - 10, y + viewer.LINE - 1)
            draw.rectangle(box, outline=HIGHLIGHT, width=2)
    return image


def teaser(folder, leak, passed):
    """Both panels side by side."""
    left, right = leak_panel(folder, leak), pass_panel(folder, passed)
    height = max(left.height, right.height)
    image = Image.new("RGB", (left.width + GAP + right.width, height), "#2b2b2b")
    image.paste(left, (0, 0))
    image.paste(right, (left.width + GAP, 0))
    return image


def write(folder, leak, passed, out=OUT):
    """Write the teaser PNG to `out`; return its path."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    teaser(folder, int(leak), int(passed)).save(out, optimize=False)
    return out


if __name__ == "__main__":
    print(write(*sys.argv[1:5]))
