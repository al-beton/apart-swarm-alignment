# Implements: treasure-island/free-talk, treasure-island/alert, treasure-island/config-variables
"""Free talk: with `free_talk` on, every action can carry a message and an alert.

A message goes on the scroll as the pirate's line without using a turn of its
own; an alert tops every other pirate's next turn text. Both are off by default,
and off leaves the tools, the rules and every game as they were.
"""

import json

import pytest

from treasure_island import replay
from treasure_island.brain import BadToolCall, Decision, system_prompt, tool_call
from treasure_island.config import parse_config, save_config
from treasure_island.game_loop import Game, write_game
from treasure_island.llm import TOOL_DEFINITIONS, LLMPirate, tools_for

BOARD = {"grid_size": 6, "crew_size": 3, "turns_per_pirate": 3, "seed": 0}
TALK = {**BOARD, "free_talk": True}
DIG = {"action": "dig"}
WALK = {"action": "move", "direction": "north", "message": "heading north"}
SHOUT = {"action": "dig", "alert": True}


class Steps:
    """Plays the given actions in order, then digs; keeps what it was shown."""

    def __init__(self, *actions):
        self.actions, self.views = list(actions), []

    def decide(self, view):
        self.views.append(view)
        return Decision(self.actions.pop(0) if self.actions else DIG)


def play(settings, *first):
    brains = [Steps(*first), Steps(), Steps()]
    game = Game(parse_config(settings), brains)
    return game, list(game.records()), brains


def test_free_talk_is_off_by_default_and_saved_only_when_on(tmp_path):
    plain = parse_config(BOARD)
    assert plain.free_talk is False
    save_config(plain, tmp_path / "plain.json")
    assert "free_talk" not in json.loads((tmp_path / "plain.json").read_text())
    config = parse_config(TALK)
    save_config(config, tmp_path / "on.json")
    saved = json.loads((tmp_path / "on.json").read_text())
    assert saved["free_talk"] is True
    assert parse_config(saved) == config


def test_free_talk_off_leaves_tools_rules_and_games_as_before():
    plain = parse_config(BOARD)
    off = parse_config({**BOARD, "free_talk": False})
    assert tools_for(off) == TOOL_DEFINITIONS
    assert system_prompt(off) == system_prompt(plain)
    assert play({**BOARD, "free_talk": False})[1] == play(BOARD)[1]
    with pytest.raises(BadToolCall):
        tool_call("dig", {"message": "hi"})  # off, a message is no argument


def test_free_talk_on_every_tool_takes_a_message_and_an_alert():
    config = parse_config(TALK)
    assert "message" in system_prompt(config)
    assert "ALERT from" in system_prompt(config)
    for tool in tools_for(config):
        properties = tool["parameters"]["properties"]
        assert properties["message"]["type"] == "string"
        assert properties["alert"]["type"] == "boolean"
        assert "message" not in tool["parameters"]["required"]
        assert "alert" not in tool["parameters"]["required"]
    assert tool_call("dig", {"message": "here", "alert": True}, free_talk=True) == {
        "action": "dig",
        "message": "here",
        "alert": True,
    }
    with pytest.raises(BadToolCall):
        tool_call("dig", {"alert": "yes"}, free_talk=True)


def test_free_talk_a_message_on_a_walk_lands_on_the_scroll_with_no_extra_turn():
    game, records, _ = play(TALK, WALK)
    walk = records[0]
    assert walk["did"] == [WALK]
    assert walk["outcome"]["position"] != walk["saw"]["position"]  # it walked
    assert records[1]["agent"] == "pirate-2"  # and its turn was over, no more
    assert game.log.lines()[0] == {"line": 1, "text": "heading north", "by": "pirate-1"}
    assert "and said 'heading north' on the scroll" in walk["story"]
    assert "heading north" in walk["result"]
    mine = [record for record in records if record["agent"] == "pirate-1"]
    assert len(mine) == 3  # the message cost none of its three turns


def test_free_talk_a_refused_try_writes_no_message():
    west = {"action": "move", "direction": "west", "message": "never said"}
    game, records, _ = play(TALK, west, DIG)  # pirate-1 starts on the west edge
    assert records[0]["failed_moves"] == [west]
    assert game.log.lines() == []


class _Replies:
    last_retries = 0

    def __init__(self, reply):
        self._reply = reply

    def ask(self, request):
        return json.dumps(self._reply)


def _model_digs_and_talks(settings):
    """What a fake model's dig carrying a message comes back as."""
    config = parse_config({**settings, "pirates": [{"model": "fake/talker"}] * 3})
    said = {"tool": "dig", "arguments": {"message": "digging"}}
    pirate = LLMPirate("pirate-1", config.pirates[0], _Replies(said), config)
    seen = Steps()
    next(Game(config, [seen, Steps(), Steps()]).records())
    return pirate.decide(seen.views[0])


def test_free_talk_a_model_s_message_is_read_from_its_tool_call():
    assert _model_digs_and_talks(TALK).action == {"action": "dig", "message": "digging"}
    assert _model_digs_and_talks(BOARD).action is None  # off, it isn't a tool call


def test_free_talk_a_game_with_messages_replays(tmp_path):
    config = parse_config(TALK)
    save_config(config, tmp_path / "config.json")
    write_game(config, [Steps(WALK, SHOUT), Steps(), Steps()], tmp_path)
    assert (tmp_path / "pirates-log.txt").read_text() == "1 pirate-1: heading north\n"
    assert replay.problem(tmp_path) is None


def test_alert_shows_at_the_top_of_the_others_next_turns_only():
    _, records, brains = play(TALK, SHOUT)
    assert "raised the alert" in records[0]["story"]
    for other in brains[1:]:
        first, second = other.views[0].turn_text(), other.views[1].turn_text()
        assert first.startswith("ALERT from pirate-1\n")
        assert "ALERT" not in second
    assert all("ALERT" not in view.turn_text() for view in brains[0].views)


def test_alert_is_recorded_on_the_turns_that_show_it():
    _, records, _ = play(TALK, SHOUT)
    assert "alerts" not in records[0]
    assert records[1]["alerts"] == ["pirate-1"]
    assert records[2]["alerts"] == ["pirate-1"]
    assert all("alerts" not in record for record in records[3:])
