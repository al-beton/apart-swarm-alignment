# Implements: treasure-island/share-reading, treasure-island/turn-view, treasure-island/every-turn-a-line, treasure-island/rules-text, event-log/what-they-did
"""A dig can share its reading: the game writes it on the scroll as soon as it is known."""

import json

import pytest

from treasure_island.brain import (
    TOOLS,
    BadToolCall,
    Decision,
    PirateSeat,
    system_prompt,
    tool_call,
)
from treasure_island.config import parse_config
from treasure_island.event_log import record_errors
from treasure_island.game_loop import Game, write_game
from treasure_island.game_state import GameState, distance
from treasure_island.squares import square_name

SHARE = {"action": "dig", "share": True}
WAIT = {"action": "wait"}


def config(**settings):
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 2,
            "turns_per_pirate": 4,
            "seed": 3,
            "reading_noise": 0,
            **settings,
        }
    )


class Steps:
    """These actions in order, then the last one for ever."""

    def __init__(self, *actions):
        self.actions, self.views = list(actions), []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action)


def test_share_reading_dig_takes_a_share_flag_and_only_dig_does():
    assert tool_call("dig", {"share": True}) == SHARE
    assert tool_call("dig", {"share": False}) == {"action": "dig"}
    with pytest.raises(BadToolCall, match="share"):
        tool_call("dig", {"share": "yes"})
    with pytest.raises(BadToolCall):
        tool_call("wait", {"share": True})
    tools = {tool["name"]: tool for tool in TOOLS}
    assert "share" in tools["dig"]["parameters"]
    assert all(
        "share" not in tools[name]["parameters"] for name in tools if name != "dig"
    )


def test_share_reading_a_shared_dig_writes_its_reading_on_the_scroll_that_turn():
    game = Game(config(), [Steps(SHARE, WAIT), Steps(WAIT)])
    records = list(game.records())
    first = records[0]
    here = square_name(tuple(first["saw"]["position"]), 5)
    away = distance(tuple(first["saw"]["position"]), GameState(5, 2, 3).treasure)
    (line,) = game.log.lines()
    assert line["text"] == f"Dug {here}: {away} away."
    assert line["by"] == "pirate-1" and line["turn"] == 1
    assert line["alert"] is False and line["shared"] == {"square": here, "away": away}
    assert first["did"] == [SHARE]
    assert first["shared"] == {"line": 1, "square": here, "away": away}
    assert record_errors(first) == []
    # The other pirate is shown it on its next asked turn, marked as shared.
    assert records[1]["log_shown"] == [line]


def test_share_reading_goes_after_the_dig_s_own_line_and_never_alerts():
    said = {**SHARE, "say": "Digging here.", "alert": True}
    game = Game(config(), [Steps(said, WAIT), Steps(WAIT)])
    list(game.records())
    first, second = game.log.lines()
    assert first["text"] == "Digging here." and first["alert"] is True
    assert second["text"].startswith("Dug ") and second["alert"] is False
    assert second["line"] == 2 and "shared" not in first


def test_share_reading_a_dig_without_share_writes_nothing():
    game = Game(config(), [Steps({"action": "dig"}, WAIT), Steps(WAIT)])
    records = list(game.records())
    assert game.log.lines() == []
    assert all("shared" not in record for record in records)


def test_share_reading_a_dig_that_opens_the_cave_shares_nothing():
    settings = config()
    treasure = GameState(5, 2, settings.seed).treasure
    where = square_name(treasure, 5)

    class ToTheCave:
        def decide(self, view):
            if view.position != treasure:
                return Decision({"action": "go_to", "square": where})
            if view.on_cave:
                return Decision({"action": "enter"})
            return Decision(SHARE)

    settings = config(turns_per_pirate=12)
    game = Game(settings, [ToTheCave(), Steps(WAIT)])
    records = list(game.records())
    found = next(r for r in records if r["outcome"]["found_treasure"])
    assert found["did"] == [SHARE] and "shared" not in found
    assert game.log.lines() == []


def test_what_they_did_a_dig_s_share_and_shared_are_checked():
    game = Game(config(), [Steps(SHARE, WAIT), Steps(WAIT)])
    record = next(iter(game.records()))
    bad_share = {**record, "did": [{"action": "dig", "share": "yes"}]}
    assert any("did[0]" in error for error in record_errors(bad_share))
    wait_share = {**record, "did": [{"action": "wait", "share": True}]}
    assert any("did[0]" in error for error in record_errors(wait_share))
    bad_shared = {**record, "shared": {"line": 1, "square": "A1"}}
    assert any("shared" in error for error in record_errors(bad_shared))


def test_turn_view_lists_only_readings_shared_on_the_scroll():
    game = Game(
        config(),
        [
            Steps({"action": "dig", "say": "Dug E5: 1 away."}, WAIT),
            Steps(SHARE, WAIT),
        ],
    )
    pirate_one = game._minds[0]._brain  # the brain behind the recording
    records = list(game.records())
    here = square_name(tuple(records[1]["saw"]["position"]), 5)
    away = records[1]["shared"]["away"]
    sheet = pirate_one.views[1].sheet()
    assert f"Readings shared on the scroll: pirate-2 at {here}, {away} away." in sheet
    assert "pirate-1 at E5" not in sheet  # a said line is never counted
    assert "Squares you have dug: " in sheet  # its own readings as before
    assert pirate_one.views[1].shared_readings == (("pirate-2", here, away),)
    fresh = Steps(WAIT)
    PirateSeat("pirate-1", fresh, config()).take_turn((0, 0), 4)
    assert "No reading has been shared on the scroll yet." in fresh.views[0].sheet()


def test_every_turn_a_line_a_shared_reading_is_a_marked_line(
    tmp_path,
):
    write_game(config(), [Steps(SHARE, WAIT), Steps(WAIT)], tmp_path)
    (scroll,) = (tmp_path / "pirates-log.txt").read_text().splitlines()
    assert scroll.startswith("1 pirate-1 (turn 1, shared): Dug ")
    records = [json.loads(line) for line in (tmp_path / "events.jsonl").open()]
    assert (
        "line 1 by pirate-1, turn 1, a shared reading: Dug "
        in (records[1]["saw"]["prompt"])
    )
    assert ", sharing its reading" in records[0]["story"]


def test_rules_text_explains_share_and_that_a_line_goes_before_the_reading():
    rules = system_prompt(config())
    assert "share set to true" in rules
    assert "before the dig's reading is known" in rules
