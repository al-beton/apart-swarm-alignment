# Implements: treasure-island/go-to, treasure-island/alert, treasure-island/wait, treasure-island/shared-squares, treasure-island/turn-order, treasure-island/say-on-any-action, treasure-island/agent-memory, treasure-island/game-ends, event-log/asked-or-walked
"""Orders: go_to walks without asking, until the pirate arrives, is blocked or an alert."""

import random

from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.event_log import record_errors
from treasure_island.game_loop import Game
from treasure_island.squares import square_name

DIG = {"action": "dig"}
WAIT = {"action": "wait"}


def go(square, **talk):
    return {"action": "go_to", "square": square, **talk}


class Steps:
    """These actions in order, then the last one for ever; counts every ask."""

    def __init__(self, *actions):
        self.actions = list(actions)
        self.views = []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action)


def config(**settings):
    # Seed 3 buries the treasure on B1, away from everyone's walks here.
    return parse_config(
        {"grid_size": 5, "crew_size": 2, "turns_per_pirate": 6, "seed": 3} | settings
    )


def play(game_config, *brains):
    return list(Game(game_config, list(brains)).records())


def of(records, name):
    return [record for record in records if record["agent"] == name]


def test_go_to_takes_its_first_step_then_walks_without_asking():
    walker = Steps(go("D5"), WAIT)
    records = play(config(turns_per_pirate=5), walker, Steps(WAIT))
    mine = of(records, "pirate-1")
    assert [r["outcome"]["position"] for r in mine[:3]] == [[1, 0], [2, 0], [3, 0]]
    assert [r["asked"] for r in mine] == [True, False, False, True, True]
    # Asked on turns 1, 4 and 5 of its own: three asks for five turns.
    assert len(walker.views) == 3
    assert mine[0]["did"] == [go("D5"), {"action": "move", "direction": "east"}]
    assert mine[1]["did"] == [{"action": "move", "direction": "east"}]
    assert mine[1]["saw"]["prompt"] == ""
    assert mine[1]["order"] == {"to": "D5", "arrived": False}
    assert mine[2]["order"] == {"to": "D5", "arrived": True}
    assert all(record_errors(record) == [] for record in records)


def test_go_to_walks_along_the_row_first_then_the_column():
    walker = Steps(go("C3"), WAIT)
    records = play(config(turns_per_pirate=5), walker, Steps(WAIT))
    steps = [r["did"][-1]["direction"] for r in of(records, "pirate-1")[:4]]
    assert steps == ["east", "east", "south", "south"]


def test_go_to_once_arrived_it_is_asked_on_its_next_turn_and_told_so():
    walker = Steps(go("C5"), WAIT)
    records = play(config(turns_per_pirate=3), walker, Steps(WAIT))
    asked = walker.views[1]
    assert asked.position == (2, 0)
    assert asked.order_ended.how == "arrived"
    assert "\nYou arrived at C5.\n" in asked.sheet()
    assert asked.earlier_turns[0].order_went == "You walked from A5 to C5 over 2 turns."
    assert of(records, "pirate-1")[2]["order_ended"] == {
        "how": "arrived",
        "to": "C5",
        "at": [2, 0],
    }
    # It was told once: the next sheet doesn't say it again.
    later = Steps(go("C5"), WAIT)
    play(config(turns_per_pirate=4), later, Steps(WAIT))
    assert later.views[2].order_ended is None


def test_go_to_one_step_away_arrives_on_its_own_turn():
    walker = Steps(go("B5"), WAIT)
    records = play(config(turns_per_pirate=2), walker, Steps(WAIT))
    assert records[0]["order"] == {"to": "B5", "arrived": True}
    assert records[2]["asked"] is True
    assert "You arrived." in records[0]["result"]


def test_shared_squares_a_blocked_step_asks_the_pirate_that_same_turn():
    # pirate-2 walks down from A4 while pirate-1 waits at A5... then pirate-1
    # walks south after it and finds pirate-2 standing on A3.
    first = Steps(WAIT, go("A1"), WAIT)
    second = Steps(go("A3"), WAIT)
    records = play(config(turns_per_pirate=4), first, second)
    # turn 0 p1 waits; 1 p2 steps to A3 (arrives); 2 p1 steps to A4;
    # 3 p2 is asked; 4 p1's next step is onto pirate-2, so it is asked.
    blocked = records[4]
    assert blocked["agent"] == "pirate-1"
    assert blocked["asked"] is True
    assert blocked["saw"]["position"] == [0, 1]
    assert blocked["order_ended"] == {
        "how": "blocked",
        "to": "A1",
        "at": [0, 1],
        "by": "pirate-2",
    }
    view = first.views[2]
    assert "You stopped at A4: the way south is blocked by pirate-2." in view.sheet()
    assert view.earlier_turns[-1].order_went == (
        "You walked from A5 to A4 over 1 turn, then stopped: the way south was "
        "blocked by pirate-2."
    )
    assert "stopped on its way to A1 as pirate-2 was in the way" in blocked["story"]


def test_alert_ends_every_other_pirate_s_order_and_asks_it_next_turn():
    walker = Steps(go("E5"), WAIT)
    shouter = Steps({"action": "wait", "say": "Stop!", "alert": True}, WAIT)
    crew = config(turns_per_pirate=5)
    records = play(crew, walker, shouter)
    # turn 0: pirate-1 sets off; turn 1: pirate-2 shouts; turn 2: pirate-1 asked.
    assert records[2]["agent"] == "pirate-1"
    assert records[2]["asked"] is True
    assert records[2]["order_ended"]["how"] == "alert"
    view = walker.views[1]
    assert view.position == (1, 0)
    assert "You stopped at B5 for an alert." in view.sheet()
    assert [line["text"] for line in view.new_lines] == ["Stop!"]
    assert view.new_lines[0]["alert"] is True
    assert view.earlier_turns[0].order_went == (
        "You walked from A5 to B5 over 1 turn, then stopped for an alert."
    )


def test_alert_a_line_without_it_does_not_wake_a_walking_pirate():
    walker = Steps(go("E5"), WAIT)
    talker = Steps({"action": "wait", "say": "just saying"}, WAIT)
    records = play(config(turns_per_pirate=5), walker, talker)
    assert [r["asked"] for r in of(records, "pirate-1")] == [
        True,
        False,
        False,
        False,
        True,
    ]
    # It sees the line when it is next asked, after it arrived.
    assert [line["text"] for line in walker.views[1].new_lines] == ["just saying"]


def test_alert_does_not_stop_the_pirate_that_raised_it():
    shouter = Steps(go("E5", say="Going east", alert=True), WAIT)
    records = play(config(turns_per_pirate=4), shouter, Steps(WAIT))
    assert [r["asked"] for r in of(records, "pirate-1")] == [True, False, False, False]


def test_say_on_any_action_only_an_action_that_happens_says_its_line():
    refused = go("A5", say="never said")
    records = play(config(turns_per_pirate=1), Steps(refused, WAIT), Steps(WAIT))
    assert records[0]["failed_moves"] == [refused]
    assert records[1]["log_shown"] == []


def test_say_on_any_action_a_pirate_can_say_as_it_enters_the_cave():
    seed = next(s for s in range(500) if _treasure(s) == (0, 0))
    entering = {"action": "enter", "say": "Cave at A5.", "alert": True}
    records = play(config(seed=seed, crew_size=2), Steps(DIG, entering), Steps(WAIT))
    assert records[2]["outcome"]["in_cave"] is True
    assert records[3]["log_shown"][0]["text"] == "Cave at A5."


def _treasure(seed):
    from treasure_island.game_state import GameState

    return GameState(5, 2, seed).treasure


def test_wait_keeps_the_pirate_where_it_is_and_asks_it_next_turn():
    waiter = Steps(WAIT)
    records = play(config(turns_per_pirate=3), waiter, Steps(WAIT))
    assert all(r["asked"] for r in records)
    assert len(waiter.views) == 3
    assert {tuple(r["outcome"]["position"]) for r in of(records, "pirate-1")} == {
        (0, 0)
    }


class Wanderer:
    """Picks any action at random from a seeded generator, talk and alerts too."""

    def __init__(self, seed, size):
        self.random, self.size = random.Random(seed), size

    def decide(self, view):
        kind = self.random.choice(["go_to", "go_to", "dig", "wait", "enter"])
        action = {"action": kind}
        if kind == "go_to":
            square = (
                self.random.randrange(self.size),
                self.random.randrange(self.size),
            )
            action["square"] = square_name(square, self.size)
        if self.random.random() < 0.3:
            action["say"] = f"line from {view.name}"
            if self.random.random() < 0.5:
                action["alert"] = True
        return Decision(action)


def test_shared_squares_never_two_pirates_on_a_square_and_the_game_always_ends():
    for seed in range(15):
        crew = parse_config(
            {"grid_size": 4, "crew_size": 5, "turns_per_pirate": 12, "seed": seed}
        )
        brains = [Wanderer(seed * 10 + n, 4) for n in range(5)]
        records = play(crew, *brains)
        assert len(records) <= 5 * 12
        assert "game_over" in records[-1]
        for record in records:
            squares = [tuple(p) for p in record["crew"].values()]
            assert len(squares) == len(set(squares))
            assert record_errors(record) == []
            if not record["asked"]:
                assert record["did"][0]["action"] == "move"
                assert all("say" not in action for action in record["did"])
