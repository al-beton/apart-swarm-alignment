# Implements: treasure-island/short-window, treasure-island/every-turn-a-line, treasure-island/reading-costs, treasure-island/read-size
"""The pirates' log: a short free window, and reading back costs the turn."""

import pytest
from treasure_island.pirate_log import LineOutOfRange, PirateLog


def line(number, text):
    return {"line": number, "text": text}


def logged(*notes, **settings):
    """A log after these turns: a note writes it, None is a turn spent elsewhere."""
    log = PirateLog(**settings)
    for note in notes:
        if note is None:
            log.blank()
        else:
            log.write(note)
    return log


def test_every_turn_a_line_a_note_when_written_and_a_blank_line_otherwise():
    log = PirateLog()
    assert log.write("Ahoy, treasure is not at (0, 0)") == 1
    assert log.blank() == 2
    assert log.write("") == 3
    assert log.lines() == [
        line(1, "Ahoy, treasure is not at (0, 0)"),
        line(2, ""),
        line(3, ""),
    ]


def test_short_window_shows_the_last_three_lines_for_free_by_default():
    log = logged("one", None, "three", "four", "five")
    assert log.shown() == [line(3, "three"), line(4, "four"), line(5, "five")]
    assert log.shown() == log.shown()
    assert len(log.lines()) == 5


def test_short_window_shows_what_there_is_when_the_log_is_shorter():
    assert PirateLog().shown() == []
    assert logged("one").shown() == [line(1, "one")]


def test_short_window_is_a_plain_value():
    assert logged("one", "two", window=1).shown() == [line(2, "two")]
    assert logged("one", "two", window=0).shown() == []


def test_read_size_returns_the_lines_around_a_chosen_line():
    log = logged("one", "two", "three", "four", "five")
    assert log.read(3) == [line(2, "two"), line(3, "three"), line(4, "four")]
    assert log.read(1) == [line(1, "one"), line(2, "two")]
    assert log.read(5) == [line(4, "four"), line(5, "five")]


def test_read_size_is_a_plain_value():
    log = logged("one", "two", "three", "four", "five", read_size=5)
    assert [shown["line"] for shown in log.read(3)] == [1, 2, 3, 4, 5]
    assert logged("one", "two", "three", read_size=1).read(2) == [line(2, "two")]


@pytest.mark.parametrize("number", [0, 6, -1, 1100])
def test_read_size_a_line_outside_the_log_gets_a_clear_answer_and_nothing_else(number):
    log = logged("one", "two", "three", "four", "five")
    with pytest.raises(LineOutOfRange) as caught:
        log.read(number)
    assert str(caught.value) == (
        f"Line {number} is outside this session's log, which has lines 1 to 5."
    )
    assert not hasattr(caught.value, "lines")


def test_read_size_an_empty_log_has_no_line_to_read():
    with pytest.raises(LineOutOfRange, match="which is empty"):
        PirateLog().read(1)


def test_reading_costs_a_read_spends_the_turn():
    log = logged("one", "two", "three")
    assert log.read(3) == [line(2, "two"), line(3, "three")]
    assert log.lines()[-1] == line(4, "")


def test_reading_costs_a_failed_read_spends_the_turn_too():
    log = logged("one", "two", "three")
    with pytest.raises(LineOutOfRange):
        log.read(9)
    assert log.lines()[-1] == line(4, "")


def test_reading_costs_the_free_window_spends_nothing():
    log = logged("one", "two", "three")
    log.shown()
    assert len(log.lines()) == 3
