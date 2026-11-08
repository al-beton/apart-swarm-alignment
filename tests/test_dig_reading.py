# Implements: treasure-island/dig-reading, treasure-island/toggles
"""Digging a square that doesn't hold the treasure says how far away it is."""

import os
import subprocess
import sys

from treasure_island.config import DEFAULTS, parse_config
from treasure_island.game_state import GameState, distance, reading


def _dig_everywhere(noise, seed=4, size=7):
    """Each square but the treasure's, with what digging it says and the truth."""
    state = GameState(size, 1, seed, noise)
    found = {}
    for x in range(size):
        for y in range(size):
            if (x, y) == state.treasure:
                continue
            state.positions = [(x, y)]
            result = state.dig()
            found[(x, y)] = (result.reading, distance((x, y), state.treasure))
    return found


def test_dig_reading_with_no_noise_is_the_true_grid_distance():
    for got, true in _dig_everywhere(0).values():
        assert got == true


def test_dig_reading_with_noise_stays_within_n_and_never_below_1():
    for noise in (1, 2, 3):
        found = _dig_everywhere(noise)
        for got, true in found.values():
            assert abs(got - true) <= noise
            assert got >= 1
        # The noise really moves some readings.
        assert any(got != true for got, true in found.values())


def test_dig_reading_tells_the_digger_in_words():
    state = GameState(5, 1, 3)
    state.positions = [(0, 0)]
    result = state.dig()
    away = distance((0, 0), state.treasure)
    assert result.message == (
        f"You dug A5 and found nothing. The treasure is {away} squares away."
    )


def test_dig_reading_one_square_away_says_square():
    state = GameState(5, 1, 3)
    x, y = state.treasure
    beside = (x + 1, y) if x < 4 else (x - 1, y)
    state.positions = [beside]
    assert state.dig().message.endswith("The treasure is 1 square away.")


def test_dig_reading_the_same_square_gives_the_same_reading_to_anyone():
    one = _dig_everywhere(2, seed=9)
    again = _dig_everywhere(2, seed=9)
    assert one == again
    assert reading(9, (1, 1), (4, 4), 2) == reading(9, (1, 1), (4, 4), 2)


def test_dig_reading_is_the_same_in_another_process_whatever_the_hash_seed():
    code = (
        "from treasure_island.game_state import reading;"
        "print([reading(5, (x, y), (3, 3), 3) for x in range(6) for y in range(6)])"
    )
    outputs = {
        subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PYTHONHASHSEED": hash_seed},
        ).stdout
        for hash_seed in ("1", "2", "3")
    }
    assert len(outputs) == 1
    assert outputs == {
        str([reading(5, (x, y), (3, 3), 3) for x in range(6) for y in range(6)]) + "\n"
    }


def test_dig_reading_noise_is_a_lever_defaulting_to_4():
    assert DEFAULTS["reading_noise"] == 4
    assert parse_config({"reading_noise": 3}).reading_noise == 3


def test_dig_reading_noise_below_0_is_rejected():
    try:
        parse_config({"reading_noise": -1})
    except ValueError as error:
        assert "reading_noise" in str(error)
    else:
        raise AssertionError("a negative reading_noise was accepted")
