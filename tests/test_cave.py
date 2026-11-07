# Implements: assets/treasure-cave, assets/hat-stack, assets/going-in
"""The treasure cave, the hat stack by its door, and a pirate going in."""

import pytest

from assets.cave import (
    GOING_IN_STEPS,
    HAT_SIZE,
    STACK_ROOM,
    cave,
    going_in,
    hat_place,
    hat_stack,
    mini_hat,
)
from assets.pirates import DEFAULT_COLOURS
from assets.pixels import SIZE, hx

CREAM = (255, 244, 214, 255)


def colours_in(image):
    return {pixel[:3] for _, pixel in image.getcolors(SIZE * SIZE) if pixel[3]}


def test_treasure_cave_is_a_square_that_glints_and_leaves_room_for_the_hats():
    frames = [cave(0), cave(1)]
    assert all(frame.size == (SIZE, SIZE) for frame in frames)
    assert frames[0].tobytes() != frames[1].tobytes()
    for frame in frames:
        assert frame.getpixel((0, 0))[3] == 0
        right = frame.crop((SIZE - 10, 0, SIZE, SIZE))
        assert right.getextrema()[3] == (0, 0), "the hat stack's side must be clear"


def test_hat_stack_is_empty_with_nobody_inside():
    assert hat_stack([]).getextrema()[3] == (0, 0)


def test_hat_stack_puts_the_first_in_at_the_bottom():
    first, second = DEFAULT_COLOURS[0], DEFAULT_COLOURS[1]
    stack = hat_stack([(first, "1"), (second, "2")])

    def lowest(colour):
        rows = [
            y
            for y in range(SIZE)
            for x in range(SIZE)
            if stack.getpixel((x, y))[:3] == hx(colour)
        ]
        return max(rows)

    assert lowest(first) > lowest(second)


def test_hat_stack_shows_every_label_for_a_crew_of_six():
    hats = [(DEFAULT_COLOURS[i], str(i + 1)) for i in range(STACK_ROOM)]
    stack = hat_stack(hats)
    for i, (colour, label) in enumerate(hats):
        hat, (x, y) = mini_hat(colour, label), hat_place(i, len(hats))
        label_rows = range(6, HAT_SIZE[1])  # the band under the brim
        for dy in label_rows:
            for dx in range(HAT_SIZE[0]):
                if hat.getpixel((dx, dy))[3]:
                    assert stack.getpixel((x + dx, y + dy)) == hat.getpixel((dx, dy))


@pytest.mark.parametrize("size", [STACK_ROOM, STACK_ROOM + 1, 20])
def test_hat_stack_keeps_a_big_crew_on_the_square(size):
    hats = [(DEFAULT_COLOURS[i % 20], str(i + 1)) for i in range(size)]
    places = [hat_place(i, size) for i in range(size)]
    assert all(y >= 0 and y + HAT_SIZE[1] <= SIZE for _, y in places)
    assert all(x >= 0 and x + HAT_SIZE[0] <= SIZE for x, _ in places)
    assert [y for _, y in places] == sorted((y for _, y in places), reverse=True)
    assert hx(hats[-1][0]) in colours_in(hat_stack(hats))


def test_hat_stack_hats_are_small_and_carry_the_label():
    hat = mini_hat("#2f6fc0", "ab")
    assert hat.size == HAT_SIZE
    assert HAT_SIZE[0] < SIZE // 2
    assert CREAM[:3] in colours_in(hat)
    assert hx("#2f6fc0") in colours_in(hat)
    with pytest.raises(ValueError):
        mini_hat("#2f6fc0", "abc")


def test_going_in_sinks_into_the_mouth_step_by_step():
    steps = [going_in(1, "#c8403c", "1", step) for step in range(GOING_IN_STEPS)]
    tops = [image.getbbox()[1] for image in steps]
    assert tops == sorted(tops) and tops[0] < tops[-1]
    assert len({image.tobytes() for image in steps}) == GOING_IN_STEPS
    with pytest.raises(ValueError):
        going_in(1, "#c8403c", "1", GOING_IN_STEPS)
