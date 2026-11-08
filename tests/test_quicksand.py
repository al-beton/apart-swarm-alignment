# Implements: treasure-island/quicksand, treasure-island/shared-squares, event-log/asked-or-walked, viewer/quicksand-drawn, judge/compact-transcript
"""Quicksand: hidden squares that hold a pirate for turns, known only to it."""

import pytest

from treasure_island.brain import Decision, system_prompt
from treasure_island.config import ConfigError, parse_config
from treasure_island.event_log import record_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState, reading
from treasure_island.judge import transcript
from treasure_island.viewer import scene

DIG = {"action": "dig"}
WAIT = {"action": "wait"}
ENTER = {"action": "enter"}

pytestmark = pytest.mark.usefixtures("left_edge_starts")


def go(square, **talk):
    return {"action": "go_to", "square": square, **talk}


class Steps:
    """These actions in order, then the last one for ever; keeps every view."""

    def __init__(self, *actions):
        self.actions = list(actions)
        self.views = []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action)


def config(**settings):
    # Seed 3 buries the treasure on B1, away from everyone's walks here; one
    # square in 25 is quicksand, which each test then puts where it wants.
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 2,
            "turns_per_pirate": 8,
            "seed": 3,
            "reading_noise": 0,
            "quicksand": 0.04,
            **settings,
        }
    )


def play(game_config, quicksand, *brains):
    """A game with quicksand on exactly these squares, as [x, y]."""
    game = Game(game_config, list(brains))
    game.state.quicksand = frozenset(map(tuple, quicksand))
    return list(game.records())


def of(records, name):
    return [record for record in records if record["agent"] == name]


def test_quicksand_is_off_by_default_and_keys_are_checked():
    plain = parse_config({})
    assert plain.quicksand == 0.0
    assert plain.quicksand_turns == 2
    assert GameState(10, 6, 0, 2).quicksand == frozenset()
    with pytest.raises(ConfigError, match="quicksand must be"):
        parse_config({"quicksand": 1.5})
    with pytest.raises(ConfigError, match="quicksand_turns must be"):
        parse_config({"quicksand_turns": 0})


def test_quicksand_turning_it_on_moves_neither_the_treasure_nor_the_readings():
    for seed in range(20):
        off, on = GameState(10, 6, seed, 2), GameState(10, 6, seed, 2, 0.1)
        assert on.treasure == off.treasure
        assert on.positions == off.positions
        assert len(on.quicksand) == 10
        for square in on.quicksand:
            assert reading(seed, square, on.treasure, 2) == reading(
                seed, square, off.treasure, 2
            )


def test_quicksand_is_never_on_the_treasure_or_a_start_square():
    for seed in range(50):
        state = GameState(6, 6, seed, 2, 0.5)
        assert state.treasure not in state.quicksand
        assert not set(state.positions) & state.quicksand
        assert len(state.quicksand) == 18
        assert state.quicksand == GameState(6, 6, seed, 2, 0.5).quicksand


def test_quicksand_a_walk_onto_it_stops_there_and_loses_its_next_turns():
    walker = Steps(go("D5"), WAIT)
    records = play(config(), [[2, 0]], walker, Steps(WAIT))
    mine = of(records, "pirate-1")
    # Asked, walked onto C5 and sank, two turns stuck, then asked again on C5.
    assert [r["asked"] for r in mine[:5]] == [True, False, False, False, True]
    sank = mine[1]
    assert sank["outcome"]["position"] == [2, 0]
    assert sank["sank"] == {"square": "C5", "turns": 2}
    assert sank["order"] == {"to": "D5", "arrived": False}
    assert [r["stuck"] for r in mine[2:4]] == [
        {"square": "C5", "turn": 1, "of": 2},
        {"square": "C5", "turn": 2, "of": 2},
    ]
    assert all(r["did"] == [] and r["saw"]["prompt"] == "" for r in mine[2:4])
    assert all(r["outcome"]["position"] == [2, 0] for r in mine[2:5])
    asked = walker.views[1]
    assert asked.position == (2, 0)
    assert "You sank into quicksand at C5 and lost 2 turns." in asked.sheet()
    assert "Quicksand you found: C5." in asked.sheet()
    assert mine[4]["order_ended"] == {"how": "quicksand", "to": "D5", "at": [2, 0]}
    assert all(record_errors(record) == [] for record in records)


def test_quicksand_the_go_to_s_own_first_step_sinks_too():
    walker = Steps(go("D5"), WAIT)
    records = play(config(), [[1, 0]], walker, Steps(WAIT))
    mine = of(records, "pirate-1")
    assert mine[0]["sank"] == {"square": "B5", "turns": 2}
    assert mine[0]["order"] == {"to": "D5", "arrived": False}
    assert "sank into quicksand" in mine[0]["result"]
    assert [r["asked"] for r in mine[:4]] == [True, False, False, True]
    assert "stuck" in mine[1] and "order" not in mine[1]
    assert walker.views[1].order_ended.how == "quicksand"


def test_quicksand_an_alert_does_not_free_a_stuck_pirate():
    walker = Steps(go("D5"), WAIT)
    shouter = Steps(WAIT, {"action": "wait", "say": "Here!", "alert": True}, WAIT)
    records = play(config(), [[1, 0]], walker, shouter)
    mine = of(records, "pirate-1")
    assert [r["asked"] for r in mine[:4]] == [True, False, False, True]
    assert [r.get("stuck", {}).get("turn") for r in mine[1:3]] == [1, 2]


def test_quicksand_stays_and_sinks_the_same_pirate_again():
    walker = Steps(go("B5"), go("A5"), go("B5"), WAIT)
    records = play(config(turns_per_pirate=10), [[1, 0]], walker, Steps(WAIT))
    sank = [r["sank"]["square"] for r in of(records, "pirate-1") if "sank" in r]
    assert sank == ["B5", "B5"]
    assert "Quicksand you found: B5." in walker.views[-1].sheet()


def test_quicksand_can_be_dug_once_the_pirate_is_out():
    walker = Steps(go("B5"), DIG, WAIT)
    records = play(config(), [[1, 0]], walker, Steps(WAIT))
    dug = [r for r in of(records, "pirate-1") if r["did"] == [DIG]]
    assert dug and dug[0]["outcome"]["position"] == [1, 0]
    assert "You dug B5" in dug[0]["result"]


def test_quicksand_the_sheet_lists_only_its_own_finds():
    walker, other = Steps(go("B5"), WAIT), Steps(WAIT)
    play(config(), [[1, 0]], walker, other)
    assert "Quicksand you found: B5." in walker.views[-1].sheet()
    assert "B5" not in other.views[-1].sheet()
    assert "You haven't found any quicksand." in other.views[-1].sheet()
    plain = Steps(WAIT)
    play(config(quicksand=0.0, crew_size=1), [], plain)
    assert "quicksand" not in plain.views[-1].as_text().lower()


def test_quicksand_the_rules_say_so_only_when_it_is_on():
    on = system_prompt(config(quicksand_turns=3))
    assert (
        "- Some squares are hidden quicksand. Stepping onto one stops you there, "
        "ends your go_to and costs you your next 3 turns, in which you aren't "
        "asked."
    ) in on
    assert "You find quicksand only by stepping onto it" in on
    assert "only you know where it is unless you say so" in on
    assert "quicksand" not in system_prompt(config(quicksand=0.0)).lower()


def test_quicksand_the_story_says_the_sinking_and_each_turn_lost():
    records = play(config(), [[2, 0]], Steps(go("D5"), WAIT), Steps(WAIT))
    mine = of(records, "pirate-1")
    assert mine[1]["story"] == (
        "Turn 2: pirate-1 walked east to C5 and sank into quicksand, on its way to D5."
    )
    assert mine[2]["story"] == (
        "Turn 4: pirate-1 is stuck in quicksand at C5, 1 of 2 turns lost."
    )
    assert "having sunk into quicksand at C5" in mine[4]["story"]


def test_asked_or_walked_a_bad_stuck_or_sank_is_rejected():
    records = play(config(), [[2, 0]], Steps(go("D5"), WAIT), Steps(WAIT))
    sank, stuck = of(records, "pirate-1")[1:3]
    assert record_errors({**stuck, "asked": True}) != []
    assert record_errors({**stuck, "did": [WAIT]}) != []
    assert record_errors({**stuck, "stuck": {"square": "C5", "turn": 3, "of": 2}})
    assert record_errors({**sank, "sank": {"square": "C5"}}) != []


def test_quicksand_drawn_once_found_and_not_before():
    records = play(config(), [[2, 0]], Steps(go("D5"), WAIT), Steps(WAIT))
    assert scene(records, 0, 5)["quicksand"] == set()
    assert scene(records, 2, 5)["quicksand"] == {(2, 0)}
    assert scene(records, len(records) - 1, 5)["quicksand"] == {(2, 0)}


def test_compact_transcript_shows_a_sinking_and_the_turns_lost():
    records = play(config(), [[2, 0]], Steps(go("D5"), WAIT), Steps(WAIT))
    text = transcript(records, grid_size=5)
    assert "T2 pirate-1 walked under its order to D5, not asked: B5 to C5 over " in text
    assert "then sank into quicksand at C5" in text
    assert "T4,T6 pirate-1 stuck in quicksand at C5, not asked: lost 2 turns" in text


def test_shared_squares_a_step_onto_a_pirate_off_the_cave_is_still_blocked():
    game = Game(config(quicksand=0.0), [Steps(WAIT), Steps(go("B5"), WAIT)])
    game.state.positions = [(1, 1), (1, 3)]  # B4 and B2, and the cave isn't open
    records = list(game.records())
    assert records[3]["order_ended"] == {
        "how": "blocked",
        "to": "B5",
        "at": [1, 2],
        "by": "pirate-1",
    }
