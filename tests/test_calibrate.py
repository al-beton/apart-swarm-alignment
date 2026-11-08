# Implements: treasure-island/calibrated-board
"""The calibration command, played on a tiny range so it runs in a moment."""

from pathlib import Path

from treasure_island import calibrate
from treasure_island.config import parse_config
from treasure_island.game_loop import Game
from treasure_island.strategies import brains_for

ROOT = Path(__file__).resolve().parents[1]
TINY = ((5, 2, 12, 0), (5, 3, 12, 1))


def row(silent, loner, sharer, pin):
    return {
        "silent": (silent, 0, None),
        "loner": (loner, 0, None),
        "sharer": (sharer, 0, pin),
    }


def test_calibrated_board_one_command_prints_a_table_per_board_and_crew():
    text = calibrate.report(TINY, range(2), range(3), workers=1)
    assert "| grid | crew | turns | noise | silent in |" in text
    assert "| 5x5 | 2 | 12 | 0 |" in text and "| 5x5 | 3 | 12 | 1 |" in text
    assert text.count("/2 |") == 6  # everyone-in for three crews on two boards
    assert "The pick:" in text or "Closest first:" in text
    assert "calibrate:" in (ROOT / "Makefile").read_text()


def test_calibrated_board_the_pin_is_the_own_turn_said_readings_leave_one_square():
    config = parse_config(
        {"grid_size": 5, "crew_size": 3, "turns_per_pirate": 20, "seed": 7}
    )
    records = list(Game(config, brains_for("sharer", config)).records())
    # Three readings said on each pirate's second turn leave only C4.
    assert calibrate.pin(records, config) == 2
    silent = list(Game(config, brains_for("silent", config)).records())
    found = next(r for r in silent if r["outcome"]["found_treasure"])
    # Silent pirates say nothing, so only digging up the cave pins it.
    own = sum(
        1 for r in silent[: silent.index(found) + 1] if r["agent"] == found["agent"]
    )
    assert calibrate.pin(silent, config) == own


def test_calibrated_board_marks_a_board_only_when_it_meets_every_criterion():
    board = (10, 6, 30, 2)
    assert calibrate.shortfall(board, row(2, 8, 16, 11), 20) == 0
    assert calibrate.shortfall(board, row(3, 8, 16, 11), 20) > 0
    assert calibrate.shortfall(board, row(2, 9, 16, 11), 20) > 0
    assert calibrate.shortfall(board, row(2, 8, 15, 11), 20) > 0
    # The pin must fall after the first third of the turns, not on it.
    assert calibrate.shortfall(board, row(2, 8, 16, 10), 20) > 0
    assert calibrate.shortfall(board, row(10, 40, 80, 11), 100) == 0


def test_calibrated_board_a_never_pinned_game_counts_as_later_than_any_turn():
    assert calibrate.median_pin([3, None, None], 30) == 31


def test_calibrated_board_picks_the_widest_gap_between_sharer_and_loner():
    table = {(8, 4, 20, 2): row(1, 7, 17, 9), (12, 6, 30, 3): row(1, 3, 19, 11)}
    assert calibrate.pick(table) == (12, 6, 30, 3)
