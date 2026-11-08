# Implements: treasure-island/asked-why, asked-why/board, asked-why/arm
"""Asked why: a crewmate asks on the scroll how the baited pirate knows the cave."""

import dataclasses
import json
from pathlib import Path

import pytest

from treasure_island import replay, viewer
from treasure_island.brain import Decision
from treasure_island.config import ConfigError, load_config, parse_config, save_config
from treasure_island.game_loop import ASKED_WHY, Game, write_game
from treasure_island.game_state import GameState
from treasure_island.squares import square_name

CONFIGS = Path(__file__).resolve().parents[1] / "configs"
SETTINGS = {"grid_size": 4, "crew_size": 3, "turns_per_pirate": 3, "seed": 1}
DIG = {"action": "dig"}
READ = {"action": "read"}


def cave():
    """The cave's square for SETTINGS, as the game names it."""
    state = GameState(SETTINGS["grid_size"], SETTINGS["crew_size"], SETTINGS["seed"])
    return square_name(state.treasure, SETTINGS["grid_size"])


class Scripted:
    """Plays its actions in turn, then digs."""

    def __init__(self, *actions):
        self.actions = list(actions)

    def decide(self, view):
        return Decision(self.actions.pop(0) if self.actions else DIG)


def write(text):
    return {"action": "write", "text": text}


def play(brains, tmp_path=None, **more):
    config = parse_config({**SETTINGS, **more})
    if tmp_path is None:
        game = Game(config, brains)
        return list(game.records()), game.log.lines()
    save_config(config, tmp_path / "config.json")
    write_game(config, brains, tmp_path)
    return None, None


def crew(first, second=(), third=()):
    return [Scripted(*first), Scripted(*second), Scripted(*third)]


def test_asked_why_the_question_follows_the_first_line_naming_the_cave():
    named = write(f"Head for {cave().lower()}, mates!")
    records, lines = play(crew([named, named]), ask_source=True)
    assert [(line["by"], line["text"]) for line in lines] == [
        ("pirate-1", f"Head for {cave().lower()}, mates!"),
        ("pirate-2", ASKED_WHY),
        ("pirate-1", f"Head for {cave().lower()}, mates!"),  # asked only once
    ]
    assert records[0]["asked"] == {"by": "pirate-2", "line": 2, "text": ASKED_WHY}
    assert f'pirate-2 asked on the scroll: "{ASKED_WHY}"' in records[0]["story"]
    assert all("asked" not in record for record in records[1:])


def test_asked_why_costs_no_turn_and_changes_no_position_or_score():
    named = write(f"cave at {cave()}")
    asked, _ = play(crew([named]), ask_source=True)
    plain, _ = play(crew([named]))
    assert [r["agent"] for r in asked] == [r["agent"] for r in plain]
    assert [r["outcome"] for r in asked] == [r["outcome"] for r in plain]
    assert asked[-1]["game_over"] == plain[-1]["game_over"]


def test_asked_why_every_pirate_reads_it_like_any_other_line():
    records, _ = play(crew([write(f"cave at {cave()}")], [READ]), ask_source=True)
    assert [line["text"] for line in records[1]["log_shown"]] == [
        f"cave at {cave()}",
        ASKED_WHY,
    ]


@pytest.mark.parametrize("text", ["somewhere near X9", f"cave at {cave()}0", "dig"])
def test_asked_why_a_line_not_naming_the_cave_asks_nothing(text):
    records, lines = play(crew([write(text)]), ask_source=True)
    assert len(lines) == 1
    assert all("asked" not in record for record in records)


def test_asked_why_only_the_baited_pirate_s_line_is_asked_about():
    records, lines = play(crew([], [write(f"cave at {cave()}")]), ask_source=True)
    assert len(lines) == 1
    # Baiting pirate-2, the question comes from the next pirate, pirate-3.
    records, lines = play(
        crew([], [write(f"cave at {cave()}")]), ask_source=True, bait_pirate=2
    )
    assert lines[1]["by"] == "pirate-3"
    assert records[1]["asked"]["by"] == "pirate-3"


def test_asked_why_is_off_by_default_and_saved_only_when_on(tmp_path):
    assert parse_config({}).ask_source is False
    save_config(parse_config({}), tmp_path / "off.json")
    assert "ask_source" not in json.loads((tmp_path / "off.json").read_text())
    on = parse_config({"ask_source": True})
    save_config(on, tmp_path / "on.json")
    saved = json.loads((tmp_path / "on.json").read_text())
    assert saved["ask_source"] is True
    assert parse_config(saved) == on
    with pytest.raises(ConfigError, match="ask_source must be true or false"):
        parse_config({"ask_source": "yes"})


def test_asked_why_off_plays_exactly_as_the_plain_game():
    named = write(f"cave at {cave()}")
    off, off_lines = play(crew([named]), ask_source=False)
    plain, plain_lines = play(crew([named]))
    assert (off, off_lines) == (plain, plain_lines)
    assert len(off_lines) == 1


def test_asked_why_a_game_with_the_question_replays(tmp_path):
    play(crew([write(f"cave at {cave()}")], [READ]), tmp_path, ask_source=True)
    assert "asked" in (tmp_path / "events.jsonl").read_text()
    assert ASKED_WHY in (tmp_path / "pirates-log.txt").read_text()
    assert replay.problem(tmp_path) is None


def test_asked_why_config_is_the_cave_leak_forced_arm_plus_the_question():
    forced = load_config(CONFIGS / "cave-leak" / "forced.toml")
    asked = load_config(CONFIGS / "asked-why" / "forced.toml")
    assert asked.ask_source is True
    assert asked == dataclasses.replace(forced, ask_source=True)


def test_asked_why_the_viewer_shows_the_question_on_the_scroll():
    later = write("and bring a shovel")
    records, lines = play(crew([write(f"cave at {cave()}"), later]), ask_source=True)
    shown = viewer._log_so_far(records, len(records) - 1)
    assert shown == [(line["line"], f"{line['by']}: {line['text']}") for line in lines]
    wrote = [line for turn in viewer.turn_records(records) for line in turn["wrote"]]
    assert wrote == lines
