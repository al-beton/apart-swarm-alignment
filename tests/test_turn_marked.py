# Implements: viewer/turn-marked
"""The pirate whose turn it is has the turn arrow over its hat, in every frame."""

from PIL import Image, ImageChops

from treasure_island import viewer

YELLOW = (255, 216, 74)  # the arrow's fill, in assets/ui.py


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
    """Whether every solid pixel of `overlay` is in `image` at `position`."""
    x, y = position
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
    return image, image.crop((0, 0, size * viewer.TILE, size * viewer.TILE))


CREW = {"pirate-1": [1, 2], "pirate-2": [3, 2]}
TWO = [
    record(0, "pirate-1", (1, 2), crew=CREW),
    record(1, "pirate-2", (3, 2), crew=CREW),
]


def test_turn_marked_every_frame_has_exactly_one_arrow_over_the_acting_pirate():
    for turn, (x, y) in ((0, (1, 2)), (1, (3, 2))):
        image, on_board = board(TWO, turn, 4)
        arrow, (left, top) = viewer.turn_arrow(viewer.scene(TWO, turn, 4))
        assert drawn_at(image, arrow, (left, top))
        assert yellow(on_board) == yellow(arrow)
        assert x * viewer.TILE <= left and left + arrow.width <= (x + 1) * viewer.TILE
        assert top + arrow.height <= y * viewer.TILE


def test_turn_marked_a_turn_with_no_speech_still_marks_the_pirate():
    silent = [record(0, "pirate-1", (2, 2), did=[])]
    image, on_board = board(silent, 0, 4)
    arrow, spot = viewer.turn_arrow(viewer.scene(silent, 0, 4))
    assert drawn_at(image, arrow, spot)
    assert yellow(on_board) == yellow(arrow)


def test_turn_marked_the_arrow_and_the_bubble_never_overlap():
    for square in ((0, 1), (2, 2), (3, 3), (1, 0)):
        records = [
            record(0, "pirate-1", square, did=[{"action": "write", "text": "x" * 40}])
        ]
        shown = viewer.scene(records, 0, 4)
        arrow, (ax, ay) = viewer.turn_arrow(shown)
        bubble = viewer.speech_bubble(shown["bubble"])
        bx, by = viewer.bubble_box(square, bubble.size, 4)
        apart = (
            ax + arrow.width <= bx
            or bx + bubble.width <= ax
            or ay + arrow.height <= by
            or by + bubble.height <= ay
        )
        assert apart, square


def test_turn_marked_the_arrow_never_covers_a_label():
    # Two pirates on one square: the second stands in front, 14 pixels lower,
    # so its arrow reaches into the first one's label, which must stay on top.
    crowd = {"pirate-1": [1, 2], "pirate-2": [1, 2]}
    records = [record(0, "pirate-2", (1, 2), crew=crowd)]
    image = viewer.frame(records, 0, 4)
    shown = viewer.scene(records, 0, 4)
    pirates = viewer._default_pirates(["pirate-1", "pirate-2"])
    for agent, spot in viewer._placed(shown):
        label = viewer._label(pirates[agent], *shown["poses"][agent])
        assert drawn_at(image, label, spot), agent
    # ...and the arrow goes where it can still be seen.
    arrow, where = viewer.turn_arrow(shown)
    assert drawn_at(image, arrow, where)
    assert yellow(image.crop((0, 0, 4 * viewer.TILE, 4 * viewer.TILE))) == yellow(arrow)


def test_turn_marked_a_crowd_on_the_top_row_still_shows_the_arrow():
    crowd = {"pirate-1": [0, 0], "pirate-2": [0, 0], "pirate-3": [0, 0]}
    for acting in crowd:
        records = [record(0, acting, (0, 0), crew=crowd)]
        image, on_board = board(records, 0, 4)
        arrow, where = viewer.turn_arrow(viewer.scene(records, 0, 4))
        assert drawn_at(image, arrow, where), acting
        assert yellow(on_board) == yellow(arrow), acting


def test_turn_marked_on_the_top_row_the_arrow_points_up_from_under_its_feet():
    top_row = [record(0, "pirate-1", (2, 0))]
    image, on_board = board(top_row, 0, 4)
    arrow, (left, top) = viewer.turn_arrow(viewer.scene(top_row, 0, 4))
    assert drawn_at(image, arrow, (left, top))
    assert yellow(on_board) == yellow(arrow)
    assert top >= viewer.TILE
    pointing_down = viewer._art("ui/turn-arrow")
    assert arrow.tobytes() == pointing_down.transpose(Image.FLIP_TOP_BOTTOM).tobytes()


def test_turn_marked_a_crowd_on_the_bottom_row_keeps_the_arrow_on_the_board():
    crowd = {f"pirate-{n}": [0, 9] for n in range(1, 7)}
    for acting in crowd:
        records = [record(0, acting, (0, 9), crew=crowd)]
        image, on_board = board(records, 0, 10)
        arrow, (left, top) = viewer.turn_arrow(viewer.scene(records, 0, 10))
        assert 0 <= top and top + arrow.height <= 10 * viewer.TILE, acting
        assert drawn_at(image, arrow, (left, top)), acting
        assert yellow(on_board) == yellow(arrow), acting
