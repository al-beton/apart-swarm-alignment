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


def record(turn, agent, at, did=(), found=False, in_cave=False, crew=None):
    outcome = {"position": list(at), "found_treasure": found}
    if in_cave:
        outcome["in_cave"] = True
    return {
        "turn": turn,
        "agent": agent,
        "saw": {"position": list(at), "prompt": ""},
        "did": list(did),
        "log_shown": [],
        "crew": crew if crew is not None else {agent: list(at)},
        "outcome": outcome,
    }


def art(name):
    return Image.open(viewer.ASSETS / f"{name}.png").convert("RGBA")


def tile(image, x, y):
    box = (x * viewer.TILE, y * viewer.TILE)
    return image.crop((*box, box[0] + viewer.TILE, box[1] + viewer.TILE)).convert("RGB")


def layered(*layers):
    ground = art("tiles/dug").copy()
    for layer in layers:
        ground.alpha_composite(layer)
    return ground.convert("RGB")


LOOKS = viewer._default_pirates(["pirate-1", "pirate-2"])


def hat(name):
    personality, colour, label = LOOKS[name]
    return (colour, label)


# Pirate 1 digs the treasure up on (1, 1) and goes in; pirate 2, on (0, 2), follows.
GAME = [
    record(
        0,
        "pirate-1",
        CAVE,
        [DIG],
        found=True,
        crew={"pirate-1": [1, 1], "pirate-2": [0, 2]},
    ),
    record(
        1, "pirate-2", (0, 2), [WEST], crew={"pirate-1": [1, 1], "pirate-2": [0, 2]}
    ),
    record(
        2,
        "pirate-1",
        CAVE,
        [ENTER],
        in_cave=True,
        crew={"pirate-1": [1, 1], "pirate-2": [0, 2]},
    ),
    record(3, "pirate-2", (0, 2), [WEST], crew={"pirate-2": [0, 2]}),
    record(4, "pirate-2", (0, 2), [WEST], crew={"pirate-2": [0, 2]}),
]


def test_cave_drawn_the_dug_up_treasure_shows_the_cave_not_an_x():
    shown = viewer.scene(GAME, 1, 3)
    assert shown["mark"] == ("cave", CAVE)
    image = viewer.frame(GAME, 1, 3)
    pirate = viewer._sprite(LOOKS["pirate-1"], *shown["poses"]["pirate-1"])
    label = viewer._label(LOOKS["pirate-1"], *shown["poses"]["pirate-1"])
    assert (
        tile(image, *CAVE).tobytes()
        == layered(art("treasure/cave-2"), pirate, label).tobytes()
    )


def test_cave_drawn_a_pirate_going_in_is_drawn_going_in_with_no_hat_yet():
    image = viewer.frame(GAME, 2, 3)
    personality, colour, label = LOOKS["pirate-1"]
    expected = layered(art("treasure/cave"), going_in(personality, colour, label, 1))
    assert tile(image, *CAVE).tobytes() == expected.tobytes()


def test_cave_drawn_after_going_in_it_is_gone_and_its_hat_is_on_the_stack():
    assert "pirate-1" not in viewer.scene(GAME, 3, 3)["positions"]
    image = viewer.frame(GAME, 3, 3)
    expected = layered(art("treasure/cave-2"), hat_stack([hat("pirate-1")]))
    assert tile(image, *CAVE).tobytes() == expected.tobytes()


def test_cave_drawn_the_gold_glints_from_one_frame_to_the_next():
    assert (
        tile(viewer.frame(GAME, 3, 3), *CAVE).tobytes()
        != tile(viewer.frame(GAME, 4, 3), *CAVE).tobytes()
    )


def test_cave_drawn_hats_stack_in_the_order_the_pirates_went_in():
    crew = {"pirate-2": [1, 1]}
    later = [
        *GAME[:3],
        record(3, "pirate-2", CAVE, [ENTER], in_cave=True, crew=crew),
        record(4, "pirate-1", (0, 0), [], crew={}),
    ]
    later[4]["agent"] = "pirate-2"
    image = viewer.frame(later, 4, 3)
    hats = hat_stack([hat("pirate-1"), hat("pirate-2")])
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
