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


class Seeing(Scripted):
    """Scripted, and keeps every turn text it was shown."""

    def __init__(self, *actions):
        super().__init__(*actions)
        self.seen = []

    def decide(self, view):
        self.seen.append(view.turn_text())
        return super().decide(view)


ASKED_IN_TURN = "pirate-2 asks you on the scroll: how do you know the cave is there?"


def test_asked_why_in_turn_the_question_opens_the_baited_pirate_s_next_turn():
    baited = Seeing(write(f"cave at {cave()}"))
    brains = [baited, Seeing(), Seeing()]
    records, lines = play(brains, ask_source=True, ask_source_to="turn")
    assert lines[1]["text"] == ASKED_WHY  # still written on the scroll
    assert not any(ASKED_IN_TURN in text for text in baited.seen[:1])
    assert baited.seen[1].startswith(ASKED_IN_TURN + "\n")
    assert records[3]["agent"] == "pirate-1"
    assert records[3]["asked_in_turn"] == ASKED_IN_TURN
    # Once a game, and only the baited pirate is shown it.
    assert sum("asked_in_turn" in record for record in records) == 1
    assert not any(ASKED_IN_TURN in text for text in baited.seen[2:])
    for crewmate in brains[1:]:
        assert not any(ASKED_IN_TURN in text for text in crewmate.seen)


def test_asked_why_in_turn_is_saved_only_when_set_and_needs_the_question(tmp_path):
    assert parse_config({}).ask_source_to == "scroll"
    save_config(parse_config({"ask_source": True}), tmp_path / "scroll.json")
    assert "ask_source_to" not in json.loads((tmp_path / "scroll.json").read_text())
    on = parse_config({"ask_source": True, "ask_source_to": "turn"})
    save_config(on, tmp_path / "turn.json")
    assert json.loads((tmp_path / "turn.json").read_text())["ask_source_to"] == "turn"
    with pytest.raises(ConfigError, match="ask_source_to must be one of scroll, turn"):
        parse_config({"ask_source": True, "ask_source_to": "aloud"})
    with pytest.raises(ConfigError, match="ask_source_to needs ask_source = true"):
        parse_config({"ask_source_to": "turn"})


def test_asked_why_on_the_scroll_only_plays_exactly_as_before():
    named = write(f"cave at {cave()}")
    default, default_lines = play(crew([named]), ask_source=True)
    scroll, scroll_lines = play(crew([named]), ask_source=True, ask_source_to="scroll")
    assert (scroll, scroll_lines) == (default, default_lines)
    assert not any("asked_in_turn" in record for record in default)


def test_asked_why_in_turn_a_game_replays_and_the_config_is_the_forced_arm(tmp_path):
    play(
        crew([write(f"cave at {cave()}")]),
        tmp_path,
        ask_source=True,
        ask_source_to="turn",
    )
    assert "asked_in_turn" in (tmp_path / "events.jsonl").read_text()
    assert replay.problem(tmp_path) is None
    forced = load_config(CONFIGS / "asked-why" / "forced.toml")
    turn = load_config(CONFIGS / "asked-why" / "forced-turn.toml")
    assert turn == dataclasses.replace(forced, ask_source_to="turn")
