# Implements: treasure-island/calibrated-board
"""The calibration command, played on a tiny range so it runs in a moment."""

from pathlib import Path

import pytest

from treasure_island import calibrate, config
from treasure_island.config import parse_config
from treasure_island.game_loop import Game
from treasure_island.strategies import brains_for

ROOT = Path(__file__).resolve().parents[1]
TINY = ((5, 2, 12, 0, 0.0), (5, 3, 12, 1, 0.0))


def row(silent, loner, sharer, pin):
    return {
        "silent": (silent, 0, None),
        "loner": (loner, 0, None),
        "sharer": (sharer, 0, pin),
    }


def test_calibrated_board_one_command_prints_a_table_per_board_and_crew():
    text = calibrate.report(TINY, range(2), range(3), workers=1)
    assert "| grid | crew | turns | noise | quicksand | silent in |" in text
    assert "| 5x5 | 2 | 12 | 0 | 0 |" in text and "| 5x5 | 3 | 12 | 1 | 0 |" in text
    assert text.count("/2 |") == 6  # everyone-in for three crews on two boards
    assert "The pick:" in text or "Closest first:" in text
    assert "calibrate:" in (ROOT / "Makefile").read_text()


def test_calibrated_board_the_pin_is_the_own_turn_shared_readings_leave_one_square():
    config = parse_config(
        {
            "grid_size": 5,
            "crew_size": 3,
            "turns_per_pirate": 20,
            "seed": 7,
            "reading_noise": 0,
        }
    )

    def shares(agent, square=None, away=None, say=None):
        record = {"agent": agent, "outcome": {"found_treasure": False}, "did": []}
        if say:
            record["did"] = [{"action": "dig", "say": say}]
        if square:
            record["shared"] = {"line": 1, "square": square, "away": away}
        return record

    # A5 and E5 each shared 3 away, which leaves only C4: pirate-2's first turn.
    records = [shares("pirate-1", "A5", 3), shares("pirate-2", "E5", 3)]
    assert calibrate.pin(records, config) == 1
    # A line in the same words, said rather than shared, doesn't count.
    said = [shares("pirate-1", "A5", 3), shares("pirate-2", say="Dug E5: 3 away.")]
    assert calibrate.pin(said, config) is None
    silent = list(Game(config, brains_for("silent", config)).records())
    found = next(r for r in silent if r["outcome"]["found_treasure"])
    # Silent pirates say nothing, so only digging up the cave pins it.
    own = sum(
        1 for r in silent[: silent.index(found) + 1] if r["agent"] == found["agent"]
    )
    assert calibrate.pin(silent, config) == own


def test_calibrated_board_marks_a_board_only_when_it_meets_every_criterion():
    board = (10, 6, 20, 2, 0.0)
    assert calibrate.shortfall(board, row(2, 8, 16, 11), 20) == 0
    assert calibrate.shortfall(board, row(3, 8, 16, 11), 20) > 0
    assert calibrate.shortfall(board, row(2, 9, 16, 11), 20) > 0
    assert calibrate.shortfall(board, row(2, 8, 15, 11), 20) > 0
    # The pin must fall after 40% of the turns and before 75%, on neither.
    assert calibrate.shortfall(board, row(2, 8, 16, 8.5), 20) == 0
    assert calibrate.shortfall(board, row(2, 8, 16, 8), 20) > 0
    assert calibrate.shortfall(board, row(2, 8, 16, 14.5), 20) == 0
    assert calibrate.shortfall(board, row(2, 8, 16, 15), 20) > 0
    assert calibrate.shortfall(board, row(2, 8, 16, 21), 20) > 0  # never pinned
    assert calibrate.shortfall(board, row(10, 40, 80, 11), 100) == 0


def test_calibrated_board_searches_the_v2_range():
    boards = set(calibrate.BOARDS)
    assert {b[0] for b in boards} == {10, 12} and {b[1] for b in boards} == {4, 6}
    assert {b[2] for b in boards} == {20, 30}
    assert {b[3] for b in boards} == {2, 3, 4, 5, (2, 5), (3, 6)}
    assert len(boards) == 48 * len(calibrate.quicksand_levels())
    banded = calibrate.config_of((10, 6, 20, (2, 5), 0.0), 0)
    assert banded.reading_bands == (2, 5) and banded.reading_noise == 0
    table = {(10, 6, 20, (2, 5), 0.0): row(0, 0, 0, 21)}
    assert "| 10x10 | 6 | 20 | bands 2/5 | 0 |" in calibrate.markdown(table, 20)


def test_calibrated_board_plays_quicksand_only_once_the_game_has_it(monkeypatch):
    if "quicksand" not in config.DEFAULTS:
        assert calibrate.quicksand_levels() == (0.0,)
        with pytest.raises(ValueError, match="quicksand"):
            calibrate.config_of((10, 6, 20, 2, 0.05), 0)
        assert calibrate.config_of((10, 6, 20, 2, 0.0), 0).grid_size == 10
    monkeypatch.setitem(config.DEFAULTS, "quicksand", 0.0)
    assert calibrate.quicksand_levels() == (0.0, 0.05, 0.10)


def test_calibrated_board_a_never_pinned_game_counts_as_later_than_any_turn():
    assert calibrate.median_pin([3, None, None], 30) == 31


def test_calibrated_board_picks_the_widest_gap_between_sharer_and_loner():
    table = {
        (10, 4, 20, 2, 0.0): row(1, 7, 17, 9),
        (12, 6, 30, 3, 0.0): row(1, 3, 19, 14),
    }
    assert calibrate.pick(table) == (12, 6, 30, 3, 0.0)


def test_calibrated_board_pins_with_bands():
    config = parse_config(
        {
            "grid_size": 5,
            "crew_size": 3,
            "turns_per_pirate": 20,
            "seed": 7,
            "reading_noise": 0,
            "reading_bands": [1, 3],
        }
    )

    def shares(agent, square, band, near, far):
        shared = {"line": 1, "square": square, "band": band, "near": near}
        return {
            "agent": agent,
            "outcome": {"found_treasure": False},
            "did": [],
            "shared": {**shared, "far": far},
        }

    # A1 hot (1 away) leaves A2 and B1, E5 cold (4 or more) keeps both, and
    # A3 hot leaves A2 alone: pirate-3's first turn.
    records = [
        shares("pirate-1", "A1", "hot", 1, 1),
        shares("pirate-2", "E5", "cold", 4, None),
        shares("pirate-3", "A3", "hot", 1, 1),
    ]
    assert calibrate.pin(records[:2], config) is None
    assert calibrate.pin(records, config) == 1
