# Implements: viewer/cave-drawn, treasure-island/treasure-mark, assets/treasure-shown
"""The viewer draws the open cave, a pirate going in, and the hats of those inside."""

from PIL import Image

from assets.cave import going_in, hat_stack
from assets.treasure import ITEMS
from treasure_island import viewer
from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState

CAVE = (1, 1)
DIG, ENTER = {"action": "dig"}, {"action": "enter"}
WEST = {"action": "move", "direction": "west"}


def record(turn, agent, at, did=(), **seen):
    """One record; `found`, `in_cave` and `crew` can be given."""
    outcome = {"position": list(at), "found_treasure": seen.get("found", False)}
    if seen.get("in_cave"):
        outcome["in_cave"] = True
    return {
        "turn": turn,
        "agent": agent,
        "saw": {"position": list(at), "prompt": ""},
        "did": list(did),
        "log_shown": [],
        "crew": seen.get("crew", {agent: list(at)}),
        "outcome": outcome,
    }


def art(name):
    return Image.open(viewer.ASSETS / f"{name}.png").convert("RGBA")


def tile(image, x, y):
    box = (viewer.EDGE_LEFT + x * viewer.TILE, y * viewer.TILE)  # in its frame
    return image.crop((*box, box[0] + viewer.TILE, box[1] + viewer.TILE)).convert("RGB")


def layered(*layers):
    ground = art("tiles/dug").copy()
    for layer in layers:
        ground.alpha_composite(layer)
    return ground.convert("RGB")


LOOKS = viewer._default_pirates(["pirate-1", "pirate-2"])


def hat(name):
    _, colour, label = LOOKS[name]
    return (colour, label)


# Pirate 1 digs the treasure up on (1, 1) and goes in. Pirate 2 stays in the far
# corner of a 4 by 4 board, so its bubble never reaches the cave's square.
FAR = (3, 3)
BOTH = {"pirate-1": [1, 1], "pirate-2": list(FAR)}
GAME = [
    record(0, "pirate-1", CAVE, [DIG], found=True, crew=BOTH),
    record(1, "pirate-2", FAR, [WEST], crew=BOTH),
    record(2, "pirate-1", CAVE, [ENTER], in_cave=True, crew=BOTH),
    record(3, "pirate-2", FAR, [WEST], crew={"pirate-2": list(FAR)}),
    record(4, "pirate-2", FAR, [WEST], crew={"pirate-2": list(FAR)}),
]


def test_cave_drawn_the_dug_up_treasure_shows_the_cave_not_an_x():
    shown = viewer.scene(GAME, 1, 4)
    assert shown["mark"] == ("cave", CAVE)
    image = viewer.frame(GAME, 1, 4)
    pirate = viewer._sprite(LOOKS["pirate-1"], *shown["poses"]["pirate-1"])
    label = viewer._label(LOOKS["pirate-1"], *shown["poses"]["pirate-1"])
    assert (
        tile(image, *CAVE).tobytes()
        == layered(art("treasure/cave-2"), pirate, label).tobytes()
    )


def test_cave_drawn_a_pirate_going_in_is_drawn_going_in_with_no_hat_yet():
    image = viewer.frame(GAME, 2, 4, step=2)  # sinking in, before its hat flies out
    personality, colour, label = LOOKS["pirate-1"]
    expected = layered(art("treasure/cave"), going_in(personality, colour, label, 1))
    # Its square is outlined as the acting pirate's, so compare inside the rim.
    rim = (3, 3, viewer.TILE - 3, viewer.TILE - 3)
    assert tile(image, *CAVE).crop(rim).tobytes() == expected.crop(rim).tobytes()


def test_cave_drawn_after_going_in_it_is_gone_and_its_hat_is_on_the_stack():
    assert "pirate-1" not in viewer.scene(GAME, 3, 4)["positions"]
    image = viewer.frame(GAME, 3, 4)
    expected = layered(art("treasure/cave-2"), hat_stack([hat("pirate-1")]))
    assert tile(image, *CAVE).tobytes() == expected.tobytes()


def test_cave_drawn_the_gold_glints_from_one_frame_to_the_next():
    assert (
        tile(viewer.frame(GAME, 3, 4), *CAVE).tobytes()
        != tile(viewer.frame(GAME, 4, 4), *CAVE).tobytes()
    )


def test_cave_drawn_hats_stack_in_the_order_the_pirates_went_in():
    # Three pirates: 1 and 2 go in, in that order, and 3 acts far away.
    looks = viewer._default_pirates(["pirate-1", "pirate-2", "pirate-3"])
    third = {"pirate-3": list(FAR)}
    records = [
        record(
            0,
            "pirate-1",
            CAVE,
            [DIG],
            found=True,
            crew={"pirate-1": [1, 1], "pirate-2": [1, 0], **third},
        ),
        record(
            1,
            "pirate-1",
            CAVE,
            [ENTER],
            in_cave=True,
            crew={"pirate-1": [1, 1], **third},
        ),
        record(
            2,
            "pirate-2",
            (1, 0),
            [{"action": "move", "direction": "south"}],
            crew={"pirate-2": [1, 0], **third},
        ),
        record(
            3,
            "pirate-2",
            CAVE,
            [ENTER],
            in_cave=True,
            crew={"pirate-2": [1, 1], **third},
        ),
        record(4, "pirate-3", FAR, [WEST], crew=third),
    ]
    records[2]["outcome"]["position"] = [1, 1]
    image = viewer.frame(records, 4, 4)
    hats = hat_stack([looks["pirate-1"][1:], looks["pirate-2"][1:]])
    assert tile(image, *CAVE).tobytes() == layered(art("treasure/cave"), hats).tobytes()


class Steps:
    def __init__(self, *actions):
        self.actions = list(actions)

    def decide(self, view):
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action)


def test_cave_drawn_the_caption_and_panel_say_how_many_are_inside():
    seed = next(s for s in range(10_000) if GameState(5, 1, s).treasure == (0, 0))
    config = parse_config(
        {"grid_size": 5, "crew_size": 2, "turns_per_pirate": 6, "seed": seed}
    )
    north = {"action": "move", "direction": "north"}
    brains = [Steps(DIG, ENTER), Steps(north, north, north, ENTER)]
    records = list(Game(config, brains).records())
    first, second = (r for r in records if r["did"] == [ENTER])
    assert "1 of 2 pirates are inside" in first["story"]
    assert "2 of 2 pirates are inside" in second["story"]
    turn = records.index(first)
    assert "1 of 2 pirates are inside" in viewer.scene(records, turn, 5)["did"]


def test_cave_drawn_the_x_is_gone_from_the_art():
    assert "mark-x" not in ITEMS
    assert not (viewer.ASSETS / "treasure/mark-x.png").exists()
