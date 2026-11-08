# Implements: treasure-island/revealed-treasure, treasure-island/cave, treasure-island/cave-queue, treasure-island/game-ends, treasure-island/score-numbers, treasure-island/actions, treasure-island/tools-only, treasure-island/failed-move
"""Digging the treasure opens a cave, and the crew goes in one by one."""

from treasure_island.brain import TOOLS, Decision, tool_call
from treasure_island.config import parse_config
from treasure_island.event_log import log_errors, record_errors
from treasure_island.game_loop import Game, write_game
from treasure_island.game_state import GameState
from treasure_island.viewer import frame, scene

DIG = {"action": "dig"}
ENTER = {"action": "enter"}
GO_A5 = {"action": "go_to", "square": "A5"}
NORTH = {"action": "move", "direction": "north"}


class Steps:
    """These actions in order, then the last one for ever."""

    def __init__(self, *actions):
        self.actions = list(actions)
        self.views = []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action)


def seed_for(square, size=5):
    return next(s for s in range(10_000) if GameState(size, 1, s).treasure == square)


def config(**settings):
    # Pirate 1 starts on (0, 0), the treasure; pirate 2 starts below it on (0, 1).
    base = {"grid_size": 5, "crew_size": 2, "turns_per_pirate": 6}
    return parse_config({**base, "seed": seed_for((0, 0)), **settings})


def play(game_config, *brains):
    return list(Game(game_config, list(brains)).records())


def test_tools_only_enter_is_the_fourth_tool():
    assert [tool["name"] for tool in TOOLS] == ["go_to", "dig", "wait", "enter"]
    assert tool_call("enter", {}) == ENTER


def test_actions_entering_is_an_action_the_event_log_takes():
    record = {
        "turn": 0,
        "agent": "pirate-1",
        "saw": {
            "position": [0, 0],
            "prompt": "",
            "neighbours": {},
            "square_dug": True,
        },
        "did": [ENTER],
        "log_shown": [],
        "outcome": {"position": [0, 0], "found_treasure": False, "in_cave": True},
    }
    assert record_errors(record) == []


def test_revealed_treasure_digging_the_treasure_opens_the_cave():
    records = play(config(crew_size=1), Steps(DIG, ENTER))
    first = records[0]
    assert first["outcome"]["found_treasure"]
    assert "cave" in first["result"]
    assert "cave" in first["story"]


def test_revealed_treasure_there_is_no_cave_until_it_is_dug():
    records = play(config(crew_size=1, turns_per_pirate=1), Steps(ENTER))
    (only,) = records
    assert only["did"] == []
    assert only["failed_moves"] == [ENTER, ENTER]
    assert "no open cave" in only["result"]


def test_revealed_treasure_only_the_pirate_on_the_cave_is_told():
    beside = Steps(DIG)
    records = play(config(), Steps(DIG, DIG), beside)
    told = [r["result"] for r in records if r["agent"] == "pirate-2"]
    assert told and all("cave" not in result for result in told)
    standing = [r["result"] for r in records if r["agent"] == "pirate-1"]
    assert "cave" in standing[1]  # digging the open cave again says it's the cave


def test_cave_entering_takes_the_pirate_out_of_the_game_for_good():
    records = play(config(), Steps(DIG, ENTER), Steps(DIG))
    entered = records[2]
    assert (entered["agent"], entered["did"]) == ("pirate-1", [ENTER])
    assert entered["outcome"]["in_cave"] is True
    later = records[3:]
    assert later and all(record["agent"] == "pirate-2" for record in later)
    assert all("pirate-1" not in record["crew"] for record in later)


def test_cave_entering_writes_nothing_on_the_scroll(tmp_path):
    write_game(config(crew_size=1), [Steps(DIG, ENTER)], tmp_path)
    assert (tmp_path / "pirates-log.txt").read_text() == ""
    assert log_errors(tmp_path / "events.jsonl") == []


def test_cave_queue_the_cave_square_holds_one_pirate_and_frees_once_it_goes_in():
    # Pirate 2 can't step onto the cave while pirate 1 stands on it, but can once
    # pirate 1 has gone in; then it enters too.
    second = Steps(GO_A5, GO_A5, GO_A5, ENTER)
    records = play(config(), Steps(DIG, ENTER), second)
    assert records[1]["agent"] == "pirate-2"
    assert records[1]["failed_moves"] == [GO_A5, GO_A5]
    assert records[3]["did"] == [GO_A5, NORTH]
    assert records[3]["outcome"]["position"] == [0, 0]
    assert records[4]["did"] == [ENTER]


def test_game_ends_when_every_pirate_is_in_the_cave():
    records = play(config(), Steps(DIG, ENTER), Steps(GO_A5, GO_A5, GO_A5, ENTER))
    over = records[-1]["game_over"]
    assert len(records) == 5
    assert over["reason"] == "everyone is in the cave"
    assert over["in_cave"] == ["pirate-1", "pirate-2"]


def test_game_ends_when_everyone_outside_has_used_their_turns():
    records = play(config(), Steps(DIG, ENTER), Steps(DIG))
    over = records[-1]["game_over"]
    assert over["reason"] == "the turns ran out"
    assert over["in_cave"] == ["pirate-1"]
    assert [r["agent"] for r in records].count("pirate-2") == 6


def test_score_numbers_each_pirate_in_the_cave_scores_100_plus_10_per_turn_left():
    # Pirate 1 enters on its 2nd of 6 turns, leaving 4: 140. Pirate 2 enters on
    # its 3rd, leaving 3: 130. The crew's score is the sum.
    records = play(config(), Steps(DIG, ENTER), Steps(GO_A5, GO_A5, GO_A5, ENTER))
    assert records[-1]["game_over"]["score"] == 140 + 130
    assert "Score 270" in records[-1]["game_over"]["story"]


def test_score_numbers_a_pirate_that_never_gets_in_adds_nothing():
    records = play(config(), Steps(DIG, ENTER), Steps(DIG))
    assert records[-1]["game_over"]["score"] == 140


def test_cave_a_pirate_that_went_in_has_left_the_board():
    records = play(config(), Steps(DIG, ENTER), Steps(DIG))
    assert "pirate-1" in scene(records, 2, 5)["positions"]  # the turn it goes in
    for turn in range(3, len(records)):
        assert set(scene(records, turn, 5)["positions"]) == {"pirate-2"}
    frame(records, len(records) - 1, 5)  # and a frame still draws


def test_turn_view_says_whether_the_pirate_stands_on_the_open_cave():
    class Recorder:
        def __init__(self, plan):
            self.plan, self.views = list(plan), []

        def decide(self, view):
            self.views.append(view)
            return Decision(self.plan.pop(0) if self.plan else {"action": "dig"})

    config = parse_config({"grid_size": 3, "crew_size": 1, "seed": 2})
    assert GameState(3, 1, 2).treasure == (0, 0)
    pirate = Recorder([{"action": "dig"}, {"action": "go_to", "square": "B3"}])
    list(Game(config, [pirate]).records())
    on_it, beside = pirate.views[1], pirate.views[2]
    assert not pirate.views[0].on_cave
    now = lambda view: view.turn_text().split("\n\n")[-1]  # this turn, not the past
    assert on_it.on_cave and "open cave" in now(on_it)
    assert not beside.on_cave and "open cave" not in now(beside)
