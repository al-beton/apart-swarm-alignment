# Implements: viewer/turn-marked
"""The pirate whose turn it is has its square outlined in yellow, in every frame."""

from PIL import Image, ImageChops

from treasure_island import viewer

YELLOW = (255, 216, 74)  # the old turn arrow's fill, in assets/ui.py
OUTLINE = (255, 210, 63)  # #ffd23f, the square's outline


def record(turn, agent, at, did=({"action": "dig"},), crew=None):
    return {
        "turn": turn,
        "agent": agent,
        "saw": {"position": list(at), "prompt": ""},
        "did": list(did),
        "log_shown": [],
        "crew": crew or {agent: list(at)},
        "outcome": {"position": list(at), "found_treasure": False},
    }


def drawn_at(image, overlay, position):
    """Whether every solid pixel of `overlay` is in the frame at board `position`."""
    x, y = position[0] + viewer.EDGE_LEFT, position[1]  # the board sits in its frame
    here = image.crop((x, y, x + overlay.width, y + overlay.height)).convert("RGB")
    solid = overlay.getchannel("A").point(lambda value: 255 if value == 255 else 0)
    wanted = Image.composite(overlay.convert("RGB"), here, solid)
    return ImageChops.difference(here, wanted).getbbox() is None


def yellow(image):
    return sum(
        1 for pixel in image.convert("RGB").get_flattened_data() if pixel == YELLOW
    )


def board(records, turn, size):
    image = viewer.frame(records, turn, size)
    grid = size * viewer.TILE
    return image, image.crop((viewer.EDGE_LEFT, 0, viewer.EDGE_LEFT + grid, grid))


CREW = {"pirate-1": [1, 2], "pirate-2": [3, 2]}
TWO = [
    record(0, "pirate-1", (1, 2), crew=CREW),
    record(1, "pirate-2", (3, 2), crew=CREW),
]


def ring(image, spot, inset):
    """The pixels of one 1-pixel rectangle `inset` inside the tile at board `spot`."""
    x, y = spot[0] + viewer.EDGE_LEFT + inset, spot[1] + inset
    far = viewer.TILE - 1 - 2 * inset
    edges = [(x + i, y) for i in range(far + 1)] + [
        (x + i, y + far) for i in range(far + 1)
    ]
    edges += [(x, y + i) for i in range(far + 1)] + [
        (x + far, y + i) for i in range(far + 1)
    ]
    return [image.getpixel(point)[:3] for point in edges]


def outlined(image, square):
    spot = (square[0] * viewer.TILE, square[1] * viewer.TILE)
    return all(
        pixel == OUTLINE for inset in range(3) for pixel in ring(image, spot, inset)
    )


def test_turn_marked_the_acting_pirate_s_square_is_outlined_in_yellow():
    image = viewer.frame(TWO, 0, 4)
    assert outlined(image, (1, 2))
    assert not outlined(image, (3, 2))


def test_turn_marked_every_frame_outlines_one_square_whoever_acts():
    for turn, square in ((0, (1, 2)), (1, (3, 2))):
        image = viewer.frame(TWO, turn, 4)
        squares = [(x, y) for x in range(4) for y in range(4)]
        assert [s for s in squares if outlined(image, s)] == [square]


def test_turn_marked_no_turn_arrow_is_drawn():
    # The arrow was the only thing in its yellow; a pirate under another's label,
    # where the arrow used to hop about, gets the outline and nothing else.
    stacked = {"pirate-1": [1, 2], "pirate-2": [1, 1]}
    image, sand = board([record(0, "pirate-1", (1, 2), crew=stacked)], 0, 4)
    assert yellow(sand) == 0
    assert outlined(image, (1, 2))
    assert not hasattr(viewer, "turn_arrow")


def test_turn_marked_the_outline_follows_a_walking_pirate():
    east = [{"action": "move", "direction": "east"}]
    walked = [
        {
            **record(0, "pirate-1", (2, 2), did=east),
            "saw": {"position": [1, 2], "prompt": ""},
        }
    ]
    halfway = viewer.frame(walked, 0, 4, step=2)
    spot = viewer.scene(walked, 0, 4, step=2)["positions"]["pirate-1"]
    pixel = (round(spot[0] * viewer.TILE), round(spot[1] * viewer.TILE))
    assert all(p == OUTLINE for p in ring(halfway, pixel, 0))
    assert outlined(viewer.frame(walked, 0, 4), (2, 2))  # it lands on its new square
