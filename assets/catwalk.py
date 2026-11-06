# Implements: assets/catwalk, assets/remade-by-one-command
"""The catwalk: every pirate walking, in one GIF: `make catwalk`.

Each pirate loops around the four squares of its own patch, so it faces every
direction and never covers a neighbour. They start at different points of the
loop, so all four directions are on show in any one frame. The ground is a
sample of the tiles a pirate can walk on.

All frames share one palette holding exactly the colours drawn, so the GIF shows
the art unchanged and the same code always writes the same bytes.
"""

import io
from pathlib import Path

from PIL import Image

from assets.pirates import DEFAULT_COLOURS, PERSONALITIES, pirate
from assets.pixels import SIZE
from assets.tiles import TILES

ASSETS = Path(__file__).resolve().parent
GROUND = ("sand", "sand-2", "grass", "sand-3", "dug")
COLUMNS = 5
_PATCH = 2 * SIZE  # the square each pirate has to itself
_STEPS_PER_SIDE = 8
_ROUTE = (("right", 1, 0), ("down", 0, 1), ("left", -1, 0), ("up", 0, -1))
LOOP = len(_ROUTE) * _STEPS_PER_SIDE
_FEET = (0, 1, 0, 2)
_FRAME_MS = 100


def walk(number, step):
    """What pirate `number` does at `step`: its pose, walking frame and [x, y]."""
    step = (step + (number - 1) * _STEPS_PER_SIDE) % LOOP
    x, y = 0, 0
    pixels = SIZE // _STEPS_PER_SIDE
    for index, (_, dx, dy) in enumerate(_ROUTE):
        done = min(max(step - index * _STEPS_PER_SIDE, 0), _STEPS_PER_SIDE)
        x, y = x + dx * done * pixels, y + dy * done * pixels
    pose = _ROUTE[step // _STEPS_PER_SIDE][0]
    column, row = (number - 1) % COLUMNS, (number - 1) // COLUMNS
    return pose, _FEET[step % len(_FEET)], [column * _PATCH + x, row * _PATCH + y]


def ground():
    """The board: the sample tiles, mixed so no two neighbours match in a row."""
    rows = (len(PERSONALITIES) + COLUMNS - 1) // COLUMNS
    across, down = COLUMNS * _PATCH // SIZE, rows * _PATCH // SIZE
    board = Image.new("RGBA", (across * SIZE, down * SIZE))
    tiles = [TILES[name]() for name in GROUND]
    for y in range(down):
        for x in range(across):
            board.paste(tiles[(x + 2 * y) % len(tiles)], (x * SIZE, y * SIZE))
    return board


def catwalk_frames():
    """Every frame of the loop, as RGBA images."""
    board = ground()
    frames = []
    for step in range(LOOP):
        frame = board.copy()
        for number in PERSONALITIES:
            pose, feet, spot = walk(number, step)
            colour = DEFAULT_COLOURS[number - 1]
            sprite = pirate(number, colour, str(number), pose, feet)
            frame.alpha_composite(sprite, tuple(spot))
        frames.append(frame)
    return frames


def _on_one_palette(frames):
    """The frames as paletted images sharing exactly the colours drawn."""
    rgb = [frame.convert("RGB") for frame in frames]
    colours = sorted({c for frame in rgb for _, c in frame.getcolors(1 << 24)})
    if len(colours) > 256:
        raise ValueError(f"A GIF holds 256 colours, and the art has {len(colours)}.")
    index = {colour: i for i, colour in enumerate(colours)}
    palette = [channel for colour in colours for channel in colour]
    paletted = []
    for frame in rgb:
        raw = frame.tobytes()
        pixels = bytes(index[tuple(raw[i : i + 3])] for i in range(0, len(raw), 3))
        image = Image.frombytes("P", frame.size, pixels)
        image.putpalette(palette)
        paletted.append(image)
    return paletted


def catwalk_gif():
    """The whole GIF, as bytes."""
    first, *rest = _on_one_palette(catwalk_frames())
    out = io.BytesIO()
    first.save(
        out,
        format="GIF",
        save_all=True,
        append_images=rest,
        duration=_FRAME_MS,
        loop=0,
        optimize=False,
    )
    return out.getvalue()


def main(folder=ASSETS):
    (Path(folder) / "catwalk.gif").write_bytes(catwalk_gif())


if __name__ == "__main__":
    main()
