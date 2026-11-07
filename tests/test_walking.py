# Implements: viewer/walks-between-squares
"""A pirate that moves walks from square to square over a few frames."""

from PIL import ImageChops

from treasure_island import viewer
from treasure_island.viewer import WALK_FRAMES

EAST = [{"action": "move", "direction": "east"}]


def turn(number, start, end, did):
    return {
        "turn": number,
        "agent": "pirate-1",
        "saw": {"position": start, "prompt": ""},
        "did": did,
        "log_shown": [],
        "outcome": {"position": end, "found_treasure": False},
    }


MOVED = [turn(0, [0, 1], [1, 1], EAST)]


def test_walks_between_squares_a_move_slides_over_4_frames():
    assert WALK_FRAMES == 4
    assert viewer.walk_steps(MOVED, 0) == [1, 2, 3, 4]
    spots = [
        viewer.scene(MOVED, 0, 3, step=s)["positions"]["pirate-1"] for s in (1, 2, 3)
    ]
    assert spots == [[0.25, 1.0], [0.5, 1.0], [0.75, 1.0]]


def test_walks_between_squares_the_last_step_is_the_turn_s_own_frame():
    last = viewer.frame(MOVED, 0, 3, step=WALK_FRAMES)
    assert last.tobytes() == viewer.frame(MOVED, 0, 3).tobytes()
    halfway = viewer.frame(MOVED, 0, 3, step=2)
    assert ImageChops.difference(halfway.convert("RGB"), last.convert("RGB")).getbbox()


def test_walks_between_squares_it_walks_on_every_in_between_frame():
    poses = [viewer.scene(MOVED, 0, 3, step=s)["poses"]["pirate-1"] for s in (1, 2, 3)]
    assert [pose for pose, _ in poses] == ["right"] * 3
    assert [feet for _, feet in poses] == [2, 1, 2]


def test_walks_between_squares_a_turn_where_nobody_moves_gets_one_frame():
    dug = [turn(0, [1, 1], [1, 1], [{"action": "dig"}])]
    assert viewer.walk_steps(dug, 0) == [None]
    # A move that failed against the edge goes nowhere, so it doesn't walk either.
    bumped = [turn(0, [0, 0], [0, 0], [{"action": "move", "direction": "north"}])]
    assert viewer.walk_steps(bumped, 0) == [None]
