# Implements: treasure-island/stated-budget, treasure-island/reasoning-memory
"""Two levers on a pirate's reasoning: the budget it's told, and how much it keeps."""

import dataclasses
import json
from pathlib import Path

import pytest

from tests.test_reasoning_budget import FakeClient, config, played
from treasure_island.brain import Decision, PirateSeat, system_prompt
from treasure_island.config import ConfigError, parse_config, save_config
from treasure_island.game_loop import Game

ROOT = Path(__file__).resolve().parent.parent


class Thinks:
    """A scripted brain that digs and thinks "thought N" on its Nth turn."""

    def __init__(self):
        self.views = []

    def decide(self, view):
        self.views.append(view)
        return Decision({"action": "dig"}, f"thought {len(self.views)}")


def five_turns(**settings):
    brain = Thinks()
    a_seat = PirateSeat("pirate-1", brain, parse_config({"grid_size": 5, **settings}))
    for turn in range(5):
        a_seat.take_turn((0, 0), 30 - turn)
        a_seat.remember(f"Dig {turn + 1}: nothing.")
    return brain.views


def test_stated_budget_a_lower_stated_budget_shows_in_the_prompt():
    told = system_prompt(config(thinking_tokens=4096, stated_thinking_tokens=3000))
    assert "You have exactly 3000 tokens to think. If you reach 3000 " in told
    assert "4096" not in told


def test_stated_budget_the_cap_sent_stays_the_real_budget(tmp_path):
    client = FakeClient()
    played(
        tmp_path,
        client,
        thinking_tokens=4096,
        stated_thinking_tokens=3000,
        reply_tokens=300,
    )
    sent = client.responses.calls[0]
    assert "exactly 3000 tokens" in sent["instructions"]
    assert sent["max_output_tokens"] == 4096 + 300


def test_stated_budget_defaults_to_the_real_budget():
    assert "exactly 2048 tokens" in system_prompt(config(thinking_tokens=2048))
    assert parse_config({}).stated_thinking_tokens is None


@pytest.mark.parametrize("stated", [5000, 0, "lots", True])
def test_stated_budget_can_t_be_more_than_the_real_one_or_not_a_number(stated):
    with pytest.raises(ConfigError, match="stated_thinking_tokens"):
        parse_config({"thinking_tokens": 4096, "stated_thinking_tokens": stated})


def test_reasoning_memory_keeps_only_the_last_n_turns_thinking():
    fifth = five_turns(reasoning_memory_turns=2)[4]
    thoughts = [turn.thinking for turn in fifth.earlier_turns]
    assert thoughts == [None, None, "thought 3", "thought 4"]
    text = fifth.as_text()
    assert "thought 3" in text and "thought 4" in text
    assert "thought 1" not in text and "thought 2" not in text


def test_reasoning_memory_older_turns_keep_everything_but_the_thinking():
    trimmed = five_turns(reasoning_memory_turns=2)[4].earlier_turns
    whole = five_turns()[4].earlier_turns
    assert [dataclasses.replace(turn, thinking=None) for turn in whole] == [
        dataclasses.replace(turn, thinking=None) for turn in trimmed
    ]
    assert "Dig 1: nothing." in trimmed[0].as_text()


def test_reasoning_memory_defaults_to_every_turn():
    fifth = five_turns()[4]
    assert [turn.thinking for turn in fifth.earlier_turns] == [
        f"thought {n}" for n in range(1, 5)
    ]
    assert parse_config({}).reasoning_memory_turns is None


def test_reasoning_memory_our_record_keeps_every_thought():
    settings = {"grid_size": 4, "crew_size": 1, "turns_per_pirate": 5}
    game = Game(parse_config({**settings, "reasoning_memory_turns": 1}), [Thinks()])
    thoughts = [record.get("thinking") for record in game.records()]
    assert [t for t in thoughts if t] == [f"thought {n}" for n in range(1, 6)]


@pytest.mark.parametrize("turns", [-1, "two", 1.5, True])
def test_reasoning_memory_must_be_a_whole_number_of_turns(turns):
    with pytest.raises(ConfigError, match="reasoning_memory_turns"):
        parse_config({"reasoning_memory_turns": turns})


# Games committed before these levers existed: their configs must not change.
EARLIER_GAMES = (
    "examples/stripes",
    "examples/llm-crew",
    "runs/reference-scribe",
    "runs/reference-silent",
    "runs/reference-stripes",
    "runs/silent-seed-7",
    "runs/readme-walkthrough",
)


def test_stated_budget_and_reasoning_memory_left_out_save_nothing(tmp_path):
    save_config(parse_config({}), tmp_path / "config.json")
    saved = json.loads((tmp_path / "config.json").read_text())
    assert "stated_thinking_tokens" not in saved
    assert "reasoning_memory_turns" not in saved
    for game in EARLIER_GAMES:
        committed = json.loads((ROOT / game / "config.json").read_text())
        resaved = tmp_path / game.replace("/", "-")
        save_config(parse_config(committed), resaved)
        assert "stated_thinking_tokens" not in resaved.read_text(), game
        assert "reasoning_memory_turns" not in resaved.read_text(), game


def test_stated_budget_and_reasoning_memory_set_are_saved_and_read_back(tmp_path):
    chosen = parse_config({"stated_thinking_tokens": 1000, "reasoning_memory_turns": 2})
    save_config(chosen, tmp_path / "config.json")
    saved = json.loads((tmp_path / "config.json").read_text())
    assert parse_config(saved) == chosen
