# Implements: treasure-island/scroll-closed
"""A config that closes the scroll: notes cost the turn and reach no one."""

import json

import pytest

from treasure_island.config import ConfigError, parse_config
from treasure_island.game_loop import write_game
from treasure_island.strategies import brains_for


def stripes(scroll):
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 3,
            "turns_per_pirate": 20,
            "seed": 7,
            "brain": "stripes",
            "scroll": scroll,
        }
    )


def played(config, folder):
    write_game(config, brains_for(config.brain, config), folder)
    rows = (folder / "events.jsonl").read_text().splitlines()
    return [json.loads(row) for row in rows]


def test_scroll_closed_the_scroll_is_open_unless_a_config_closes_it():
    assert parse_config({}).scroll is True
    assert parse_config({"scroll": False}).scroll is False
    with pytest.raises(ConfigError, match="scroll must be true or false"):
        parse_config({"scroll": "no"})


def test_scroll_closed_a_note_reaches_no_one_and_reads_find_nothing(tmp_path):
    (tmp_path / "open").mkdir()
    (tmp_path / "closed").mkdir()
    opened = played(stripes(True), tmp_path / "open")
    closed = played(stripes(False), tmp_path / "closed")
    assert (tmp_path / "open" / "pirates-log.txt").read_text()
    assert (tmp_path / "closed" / "pirates-log.txt").read_text() == ""
    writes = [r for r in closed if r["did"] and r["did"][0]["action"] == "write"]
    assert writes, "the striping pirates still try to write"
    assert all("the scroll is closed" in r["result"].lower() for r in writes)
    assert all("the scroll is closed" in r["story"] for r in writes)
    assert all(r["log_shown"] == [] for r in closed)
    assert any(r["log_shown"] for r in opened)
