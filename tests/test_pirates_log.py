# Implements: treasure-island/short-window, treasure-island/every-turn-a-line, treasure-island/reading-costs, treasure-island/read-size
"""The pirates' log: a short free window, and reading back costs a turn."""

import pytest

from treasure_island.event_log import record_errors
from treasure_island.pirates_log import PiratesLog


def log_with(count, **sizes):
    log = PiratesLog(**sizes)
    for number in range(1, count + 1):
        log.write(f"note {number}")
    return log


def numbers(lines):
    return [line["line"] for line in lines]


def test_every_turn_a_line_a_written_note_is_the_line():
    log = PiratesLog()
    log.write("digging at (2, 3)")
    assert log.window() == [{"line": 1, "text": "digging at (2, 3)"}]


def test_every_turn_a_line_any_other_turn_adds_a_blank_line():
    log = PiratesLog()
    log.pass_turn()
    assert log.window() == [{"line": 1, "text": ""}]


def test_every_turn_a_line_a_note_stays_on_one_line():
    log = PiratesLog()
    log.write("first\nsecond")
    log.write("third")
    assert log.window() == [
        {"line": 1, "text": "first second"},
        {"line": 2, "text": "third"},
    ]


def test_every_turn_a_line_lines_fit_the_event_log_format():
    log = log_with(4)
    record = {
        "turn": 0,
        "agent": "pirate-a",
        "saw": {"position": [0, 0], "prompt": ""},
        "did": [],
        "log_shown": [*log.window(), *log.read(1).lines],
        "outcome": {"position": [0, 0], "found_treasure": False},
    }
    assert record_errors(record) == []


def test_short_window_shows_the_last_3_lines_by_default():
    assert numbers(log_with(5).window()) == [3, 4, 5]


def test_short_window_shows_what_there_is_early_on():
    assert log_with(0).window() == []
    assert numbers(log_with(2).window()) == [1, 2]


def test_short_window_size_is_a_plain_value():
    assert numbers(log_with(6, window=4).window()) == [3, 4, 5, 6]


def test_short_window_of_zero_shows_nothing():
    assert log_with(5, window=0).window() == []


def test_short_window_costs_no_turn():
    log = log_with(5)
    log.window()
    assert numbers(log.window()) == [3, 4, 5]


def test_reading_costs_a_read_spends_the_turn_on_a_blank_line():
    log = log_with(5)
    log.read(1)
    assert log.window() == [
        {"line": 4, "text": "note 4"},
        {"line": 5, "text": "note 5"},
        {"line": 6, "text": ""},
    ]


def test_reading_costs_a_read_outside_the_log_still_spends_the_turn():
    log = log_with(5)
    log.read(99)
    assert numbers(log.window()) == [4, 5, 6]


def test_read_size_returns_the_3_lines_around_a_line_by_default():
    answer = log_with(9).read(5)
    assert answer.lines == [
        {"line": 4, "text": "note 4"},
        {"line": 5, "text": "note 5"},
        {"line": 6, "text": "note 6"},
    ]
    assert answer.message == ""


@pytest.mark.parametrize(
    "line, expected",
    [(1, [1, 2, 3]), (2, [1, 2, 3]), (8, [7, 8, 9]), (9, [7, 8, 9])],
)
def test_read_size_stays_full_at_either_end_of_the_log(line, expected):
    assert numbers(log_with(9).read(line).lines) == expected


def test_read_size_is_a_plain_value():
    assert numbers(log_with(9, read_size=5).read(5).lines) == [3, 4, 5, 6, 7]
    assert numbers(log_with(9, read_size=1).read(5).lines) == [5]
    assert numbers(log_with(9, read_size=2).read(5).lines) == [5, 6]


def test_read_size_a_log_shorter_than_a_read_returns_all_of_it():
    assert numbers(log_with(2).read(1).lines) == [1, 2]


@pytest.mark.parametrize("line", [-1, 0, 6, 1100])
def test_read_size_a_line_outside_the_log_gets_a_clear_answer_and_no_data(line):
    answer = log_with(5).read(line)
    assert answer.lines == []
    assert str(line) in answer.message
    assert "note" not in answer.message


def test_read_size_reading_an_empty_log_gets_a_clear_answer():
    answer = PiratesLog().read(1)
    assert answer.lines == []
    assert answer.message
