# Implements: assets/scroll-held
"""A pirate reading or writing holds the open scroll in front of it."""

import pytest

from assets.pirates import DEFAULT_COLOURS, PERSONALITIES, pirate
from assets.pixels import SIZE, hx

PARCHMENT = hx("#f0e2bc")
INK = hx("#2a1a28")


def colours_in(image, box):
    region = image.crop(box)
    return {p[:3] for _, p in region.getcolors(SIZE * SIZE) if p[3]}


@pytest.mark.parametrize("pose", ["read", "write"])
def test_scroll_held_every_pirate_reads_and_writes_in_front_of_its_coat(pose):
    for n in PERSONALITIES:
        colour = DEFAULT_COLOURS[n - 1]
        sprite = pirate(n, colour, str(n), pose, 0)
        standing = pirate(n, colour, str(n), "down", 0)
        chest = (14, 31, 34, 40)
        assert PARCHMENT in colours_in(sprite, chest), n
        assert sprite.crop(chest).tobytes() != standing.crop(chest).tobytes(), n


def test_scroll_held_the_written_line_grows_frame_by_frame():
    frames = [pirate(1, "#c8403c", "1", "write", f) for f in range(3)]
    row = 29 + 10  # the line being written
    inked = [
        sum(frame.getpixel((x, row))[:3] == INK for x in range(15, 34))
        for frame in frames
    ]
    assert inked == sorted(inked) and inked[0] < inked[-1]
    reading = [pirate(1, "#c8403c", "1", "read", f) for f in range(2)]
    assert reading[0].tobytes() != reading[1].tobytes()


@pytest.mark.parametrize("pose", ["read", "write"])
def test_scroll_held_the_face_and_label_stay_above_the_scroll(pose):
    for frame in range(3 if pose == "write" else 2):
        sprite = pirate(5, "#2f6fc0", "12", pose, frame)
        standing = pirate(5, "#2f6fc0", "12", "down", 0)
        head = (12, 0, 36, 23)  # the quill's feather may cross the chin
        assert sprite.crop(head).tobytes() == standing.crop(head).tobytes()
