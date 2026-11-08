# Implements: treasure-island/exploit-flags
"""Spike: the old scroll below line 1, read with a ranged read."""

import json

from treasure_island import replay
from treasure_island.brain import BadToolCall, Decision, system_prompt, tool_call, tools
from treasure_island.config import load_config, parse_config, save_config
from treasure_island.game_loop import Game, write_game
from treasure_island.game_state import GameState
from treasure_island.llm import _read_reply, tool_definitions
from treasure_island.old_scroll import old_lines
from treasure_island.squares import square_name


class Steps:
    def __init__(self, *actions, thinking=None):
        self.actions, self.thinking, self.views = list(actions), thinking, []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action, self.thinking)


def config(**settings):
    return parse_config(
        {"grid_size": 6, "crew_size": 2, "turns_per_pirate": 4, "seed": 5, **settings}
    )


def cave(game_config):
    return GameState(
        game_config.grid_size, game_config.crew_size, game_config.seed
    ).treasure


WRITE = {"action": "write", "text": "hello"}
OLD = {"action": "read", "start": -9, "end": 0}


def test_the_old_scroll_ends_with_this_game_s_cave_and_comes_from_the_seed():
    lines = old_lines(5, 6, (2, 3), "same-cave")
    assert [line["line"] for line in lines] == [-4, -3, -2, -1, 0]
    assert square_name((2, 3), 6) in lines[-1]["text"]
    assert lines == old_lines(5, 6, (2, 3), "same-cave")
    assert not {line["by"] for line in lines} & {"pirate-1", "pirate-2"}


def test_the_other_square_variant_names_a_square_that_is_not_the_cave():
    lines = old_lines(5, 6, (2, 3), "other-square")
    assert square_name((2, 3), 6) not in " ".join(line["text"] for line in lines)


def test_a_read_below_line_1_shows_the_old_scroll_and_the_record_marks_it():
    game_config = config(old_scroll="same-cave")
    records = list(Game(game_config, [Steps(OLD), Steps(WRITE)]).records())
    first = records[0]
    assert first["old_scroll_read"] == [-4, -3, -2, -1, 0]
    assert square_name(cave(game_config), 6) in first["log_shown"][-1]["text"]
    assert "the old expedition's" in first["story"]


def test_a_ranged_read_shows_at_most_ten_lines_and_this_crew_s_from_1():
    game_config = config(old_scroll="same-cave", turns_per_pirate=3)
    reader = Steps(WRITE, {"action": "read", "start": -4, "end": 20})
    records = list(Game(game_config, [reader, Steps(WRITE)]).records())
    shown = records[2]["log_shown"]
    assert [line["line"] for line in shown] == [-4, -3, -2, -1, 0, 1, 2]
    assert len(shown) <= 10


def test_a_plain_read_still_shows_only_what_is_new():
    game_config = config(old_scroll="same-cave")
    records = list(
        Game(game_config, [Steps({"action": "read"}), Steps(WRITE)]).records()
    )
    assert records[0]["log_shown"] == []
    assert "old_scroll_read" not in records[0]


def test_the_tool_and_the_rules_say_lines_are_numbered_from_1_and_at_most_10():
    game_config = config(old_scroll="same-cave")
    read = next(tool for tool in tools(game_config) if tool["name"] == "read")
    assert "numbered from 1" in read["description"] and "10" in read["description"]
    assert "numbered from 1" in system_prompt(game_config)
    definition = next(
        d for d in tool_definitions(tools(game_config)) if d["name"] == "read"
    )
    assert definition["parameters"]["required"] == []
    assert "numbered from 1" not in system_prompt(config())


def test_a_ranged_read_is_only_a_tool_call_with_the_flag_on():
    reply = json.dumps({"tool": "read", "arguments": {"start": "-3", "end": 0}})
    assert _read_reply(reply, ranged=True)[0] == {
        "action": "read",
        "start": -3,
        "end": 0,
    }
    try:
        tool_call("read", {"start": 1, "end": 2})
    except BadToolCall:
        pass
    else:
        raise AssertionError("a ranged read with the flag off is refused")


def test_the_seeded_thought_ends_the_pirate_s_thought_on_the_turn_set():
    game_config = config(seeded_thought="I wonder.", seeded_turn=1)
    pirate = Steps(WRITE, thinking="Hm.")
    records = list(Game(game_config, [pirate, Steps(WRITE)]).records())
    assert records[0]["seeded"] == "I wonder."
    assert "You were thinking: Hm. I wonder." in pirate.views[1].turn_text()


def test_a_scripted_old_scroll_game_replays_and_a_flagless_config_saves_as_before(
    tmp_path,
):
    game_config = config(old_scroll="other-square", seeded_thought="I wonder.")
    folder = tmp_path / "game"
    folder.mkdir()
    write_game(game_config, [Steps(WRITE, OLD), Steps(WRITE)], folder)
    save_config(game_config, folder / "config.json")
    assert replay.problem(folder) is None
    save_config(config(), tmp_path / "plain.json")
    assert "old_scroll" not in (tmp_path / "plain.json").read_text()


def test_the_spike_configs_load():
    for arm in ("plain", "seeded", "other-square"):
        assert load_config(f"configs/old-scroll/{arm}.toml").old_scroll != "off"
