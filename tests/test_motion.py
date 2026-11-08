# Implements: assets/board-edges, assets/dig-motion, assets/enter-motion
"""The board's chess-named frame, the dig over six steps, and going into the cave."""

import pytest

from assets.board import EDGE_BOTTOM, EDGE_LEFT, board_edges, column_letter
from assets.cave import ENTER_STEPS, cave, entering, hat_place, hat_stack, mini_hat
from assets.dig import DIG_STEPS, dig_ground, digging
from assets.pirates import pirate
from assets.pixels import SIZE
from assets.tiles import TILES


def same(a, b):
    return a.tobytes() == b.tobytes()


def test_board_edges_frame_the_board_and_leave_it_clear():
    edges = board_edges(5)
    assert edges.size == (5 * SIZE + EDGE_LEFT, 5 * SIZE + EDGE_BOTTOM)
    board = edges.crop((EDGE_LEFT, 0, edges.width, 5 * SIZE))
    assert board.getextrema()[3] == (0, 0), "the board itself is left clear"
    assert edges.getpixel((0, 0))[3] == 255
    assert edges.getpixel((0, edges.height - 1))[3] == 255


def test_board_edges_label_every_column_and_row():
    edges = board_edges(10)
    grid = 10 * SIZE
    blank = board_edges(1).getpixel((1, 1))  # bare wood
    for i in range(10):
        under = edges.crop(
            (EDGE_LEFT + i * SIZE, grid, EDGE_LEFT + (i + 1) * SIZE, edges.height)
        )
        beside = edges.crop((0, i * SIZE, EDGE_LEFT, (i + 1) * SIZE))
        for strip in (under, beside):
            assert any(p != blank for _, p in strip.getcolors(SIZE * SIZE)), i


def test_board_edges_name_columns_a_onward_and_reject_too_wide():
    assert [column_letter(x) for x in (0, 4, 25)] == ["A", "E", "Z"]
    assert board_edges(26).width == 26 * SIZE + EDGE_LEFT
    with pytest.raises(ValueError):
        board_edges(27)


def test_dig_motion_turns_sand_to_dug_and_ends_on_the_still_pose():
    assert same(dig_ground(0), TILES["sand"]())
    assert same(dig_ground(0, TILES["sand-2"]()), TILES["sand-2"]())
    assert same(dig_ground(DIG_STEPS - 1), TILES["dug"]())
    look = (2, "#2f6fc0", "2")
    assert same(digging(*look, DIG_STEPS - 1), pirate(*look, "dig", 0))
    steps = [digging(*look, step) for step in range(DIG_STEPS)]
    assert len({image.tobytes() for image in steps}) == DIG_STEPS
    with pytest.raises(ValueError):
        digging(*look, DIG_STEPS)


def test_dig_motion_throws_sand_above_the_pirate():
    look = (2, "#2f6fc0", "2")
    still = pirate(*look, "dig", 0)
    high = digging(*look, 3)
    assert high.getbbox()[1] <= still.getbbox()[1], "the sand flies over its hat"


def test_enter_motion_sinks_then_flies_the_hat_onto_the_stack():
    inside = [("#c8403c", "1"), ("#3c9a4a", "3")]
    look = (4, "#e08a2c", "4")
    steps = [entering(*look, inside, step) for step in range(ENTER_STEPS)]
    assert len({image.tobytes() for image in steps}) == ENTER_STEPS
    before = cave(0)
    before.alpha_composite(hat_stack(inside))
    after = cave(ENTER_STEPS - 1 >> 1 & 1)
    after.alpha_composite(hat_stack([*inside, ("#e08a2c", "4")]))
    assert same(steps[-1], after), "the last step is the square as the next turn has it"
    x, y = hat_place(len(inside), len(inside) + 1)
    hat = mini_hat("#e08a2c", "4")
    landed = steps[ENTER_STEPS - 3].crop((x, y, x + hat.width, y + hat.height))
    flying = steps[4].crop((x, y, x + hat.width, y + hat.height))
    assert not same(flying, landed), "the hat is still in the air before it lands"
    with pytest.raises(ValueError):
        entering(*look, inside, ENTER_STEPS)
