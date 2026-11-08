# Implements: viewer/board-framed, viewer/dig-steps, viewer/enter-steps
"""The board in its chess-named frame, a dig in six steps and going in in nine."""

from PIL import Image

from assets.board import EDGE_BOTTOM, EDGE_LEFT, board_edges
from assets.cave import ENTER_STEPS, entering, hat_stack
from assets.dig import DIG_STEPS, dig_ground, digging
from treasure_island import viewer
from treasure_island.squares import square_name

TILE = viewer.TILE
CAVE = (1, 1)
LOOKS = viewer._default_pirates(["pirate-1", "pirate-2"])


def record(turn, agent, at, did=(), **seen):
    outcome = {"position": list(at), "found_treasure": seen.get("found", False)}
    if seen.get("in_cave"):
        outcome["in_cave"] = True
    return {
        "turn": turn,
        "agent": agent,
        "saw": {"position": list(at), "prompt": ""},
        "did": [{"action": action} for action in did],
        "log_shown": [],
        "crew": seen.get("crew", {agent: list(at)}),
        "outcome": outcome,
    }


def art(name):
    return Image.open(viewer.ASSETS / f"{name}.png").convert("RGBA")


def square(image, x, y):
    """One board square of a frame, the board sitting inside its frame."""
    left, top = EDGE_LEFT + x * TILE, y * TILE
    return image.crop((left, top, left + TILE, top + TILE)).convert("RGB")


def inside(tile):
    """A tile without its 3-pixel rim, where the acting pirate's outline goes."""
    rim = 3
    return tile.crop((rim, rim, TILE - rim, TILE - rim)).tobytes()


def over(ground, *layers):
    ground = ground.copy()
    for layer in layers:
        ground.alpha_composite(layer)
    return ground.convert("RGB")


STILL = [record(0, "pirate-1", (1, 1))]
FAR = (3, 3)
BOTH = {"pirate-1": list(CAVE), "pirate-2": list(FAR)}
# Pirate 2 digs on sand, pirate 1 digs the treasure up and goes in, on a 4 by 4 board.
GAME = [
    record(0, "pirate-2", FAR, ["dig"], crew=BOTH),
    record(1, "pirate-1", CAVE, ["dig"], found=True, crew=BOTH),
    record(2, "pirate-2", FAR, ["dig"], crew=BOTH),
    record(3, "pirate-1", CAVE, ["enter"], in_cave=True, crew=BOTH),
    record(4, "pirate-2", FAR, ["dig"], crew={"pirate-2": list(FAR)}),
]


def test_board_framed_no_square_names_on_the_sand():
    image = viewer.frame(STILL, 0, 3)
    for x in range(3):
        for y in range(3):
            if (x, y) in ((1, 1), (1, 0)):
                continue  # the pirate's outlined square, and the one above it
            tile = art(f"tiles/{viewer._ground_tile(x, y)}").convert("RGB")
            assert square(image, x, y).tobytes() == tile.tobytes()


def test_board_framed_the_frame_is_on_every_frame_and_names_match():
    edges = board_edges(4)
    grid = 4 * TILE
    for turn in range(len(GAME)):
        for step in viewer.turn_steps(GAME, turn):
            image = viewer.frame(GAME, turn, 4, step=step).convert("RGBA")
            framed = image.crop((0, 0, edges.width, edges.height))
            # Wherever the frame has paint, the image has the frame's own pixels.
            left = framed.crop((0, 0, EDGE_LEFT, grid))
            below = framed.crop((0, grid, edges.width, edges.height))
            assert left.tobytes() == edges.crop((0, 0, EDGE_LEFT, grid)).tobytes()
            under = edges.crop((0, grid, edges.width, edges.height))
            assert below.tobytes() == under.tobytes()
    assert edges.height == grid + EDGE_BOTTOM
    # The frame's letters and numbers are the squares' names: A1 is the bottom left.
    assert square_name((0, 3), 4) == "A1"
    assert square_name((3, 0), 4) == "D4"


def test_dig_steps_a_dig_takes_6_steps():
    assert DIG_STEPS == 6
    assert viewer.turn_steps(GAME, 0) == [1, 2, 3, 4, 5, 6]
    shown = viewer.scene(GAME, 0, 4, step=3)
    assert shown["digging"] == (2, viewer._ground_tile(*FAR))


def test_dig_steps_the_ground_turns_to_dug_sand():
    look = LOOKS["pirate-2"]
    sand = art(f"tiles/{viewer._ground_tile(*FAR)}")
    for step in range(1, DIG_STEPS):
        image = viewer.frame(GAME, 0, 4, step=step)
        expected = over(dig_ground(step - 1, sand), digging(*look, step - 1))
        assert inside(square(image, *FAR)) == inside(expected)
    # It starts on its own sand and ends on dug sand.
    assert dig_ground(0, sand).tobytes() == sand.tobytes()
    last = square(viewer.frame(GAME, 0, 4, step=DIG_STEPS), *FAR)
    pose = viewer.scene(GAME, 0, 4)["poses"]["pirate-2"]
    sprite = viewer._sprite(look, *pose)
    label = viewer._label(look, *pose)
    assert inside(last) == inside(over(art("tiles/dug"), sprite, label))


def test_dig_steps_the_last_step_is_the_turn_s_own_frame():
    last = viewer.frame(GAME, 0, 4, step=DIG_STEPS)
    assert last.tobytes() == viewer.frame(GAME, 0, 4).tobytes()
    assert viewer.scene(GAME, 0, 4, step=DIG_STEPS)["digging"] is None
    # The dig that finds the treasure ends on the cave, not before.
    assert viewer.scene(GAME, 1, 4, step=3)["mark"] != ("cave", CAVE)
    assert viewer.scene(GAME, 1, 4, step=DIG_STEPS)["mark"] == ("cave", CAVE)


def test_enter_steps_going_in_takes_9_steps():
    assert ENTER_STEPS == 9
    assert viewer.turn_steps(GAME, 3) == list(range(1, ENTER_STEPS + 1))


def test_enter_steps_the_pirate_sinks_then_its_hat_flies_onto_the_stack():
    look = LOOKS["pirate-1"]
    drawn = []
    for step in range(1, ENTER_STEPS + 1):
        image = viewer.frame(GAME, 3, 4, step=step)
        expected = over(art("tiles/dug"), entering(*look, [], step - 1))
        assert inside(square(image, *CAVE)) == inside(expected)
        drawn.append(inside(square(image, *CAVE)))
    # It sinks over the first 4 steps, so it's gone from the board after step 3...
    empty = over(art("tiles/dug"), entering(*look, [], 4))
    assert drawn[4] != drawn[3]
    assert inside(empty) == drawn[4]
    # ...and its hat is on the stack in the last.
    stacked = over(art("tiles/dug"), art("treasure/cave"), hat_stack([look[1:]]))
    assert drawn[-1] == inside(stacked)


def test_enter_steps_the_last_step_is_the_turn_s_own_frame():
    last = viewer.frame(GAME, 3, 4, step=ENTER_STEPS)
    assert last.tobytes() == viewer.frame(GAME, 3, 4).tobytes()
    # The next turn draws the cave the same, its gold on the same glint frame here.
    after = viewer.frame(GAME, 4, 4)
    # Only the outline differs: the cave square is no longer the acting pirate's.
    assert inside(square(after, *CAVE)) == inside(square(last, *CAVE))


def drawn_dig(game, turn, step, before, draw):
    """The digger's square as it should be: the dig's ground, `draw` over it, then
    the digging pirate on top."""
    x, y = game[turn]["saw"]["position"]
    board = Image.new("RGB", (4 * TILE, 4 * TILE))
    board.paste(dig_ground(step - 1, art(f"tiles/{before}")), (x * TILE, y * TILE))
    draw(board, viewer.scene(game, turn, 4, CAVE, step=step))
    ground = board.crop((x * TILE, y * TILE, (x + 1) * TILE, (y + 1) * TILE))
    look = LOOKS[game[turn]["agent"]]
    return over(ground.convert("RGBA"), digging(*look, step - 1))


def test_dig_steps_the_question_mark_stays_over_the_ground_on_every_step():
    # The digger stands on the mark and hides it, so look at the ground it stands on.
    sand = art(f"tiles/{viewer._ground_tile(*CAVE)}")
    x, y = CAVE
    for step in range(1, DIG_STEPS):
        shown = viewer.scene(GAME, 1, 4, CAVE, step=step)
        assert shown["mark"] == ("mark-question", CAVE)
        board = Image.new("RGB", (4 * TILE, 4 * TILE))
        viewer._draw_ground(board, 4, shown, LOOKS)
        ground = board.crop((x * TILE, y * TILE, (x + 1) * TILE, (y + 1) * TILE))
        expected = over(dig_ground(step - 1, sand), art("treasure/mark-question"))
        assert ground.tobytes() == expected.tobytes()


def test_dig_steps_the_open_cave_and_its_hats_stay_over_the_ground_on_every_step():
    # Pirate 1 opens the cave and goes in; pirate 2 then stands on it and digs.
    game = [
        *GAME[:2],
        record(2, "pirate-1", CAVE, ["enter"], in_cave=True, crew=BOTH),
        record(3, "pirate-2", CAVE, ["dig"], crew={"pirate-2": list(CAVE)}),
    ]
    assert viewer.scene(game, 3, 4, CAVE)["inside"] == ["pirate-1"]

    def cave(board, shown):
        viewer._draw_cave(board, shown, LOOKS)

    for step in range(1, DIG_STEPS):
        image = viewer.frame(game, 3, 4, None, CAVE, step)
        expected = drawn_dig(game, 3, step, "dug", cave)
        assert inside(square(image, *CAVE)) == inside(expected)


READ = [record(0, "pirate-2", FAR, ["read"], crew=BOTH)]
WRITE = [
    {
        **record(0, "pirate-2", FAR, ["dig"], crew=BOTH),
        "did": [{"action": "write", "text": "Over here"}],
    }
]


def test_scroll_steps_a_read_takes_2_steps_and_a_write_3():
    assert viewer.turn_steps(READ, 0) == [1, 2]
    assert viewer.turn_steps(WRITE, 0) == [1, 2, 3]


def test_scroll_steps_each_step_shows_the_next_frame_of_the_pose():
    for records, pose, frames in ((READ, "read", 2), (WRITE, "write", 3)):
        poses = [
            viewer.scene(records, 0, 4, step=step)["poses"]["pirate-2"]
            for step in range(1, frames + 1)
        ]
        assert poses == [(pose, frame) for frame in range(frames)]
        drawn = {
            inside(square(viewer.frame(records, 0, 4, step=step), *FAR))
            for step in range(1, frames + 1)
        }
        assert len(drawn) == frames  # the scroll moves, step by step


def test_scroll_steps_the_last_step_is_the_turn_s_own_frame():
    for records, frames in ((READ, 2), (WRITE, 3)):
        last = viewer.frame(records, 0, 4, step=frames)
        assert last.tobytes() == viewer.frame(records, 0, 4).tobytes()
