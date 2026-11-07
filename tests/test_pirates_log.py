# Implements: treasure-island/every-turn-a-line, treasure-island/reading-costs
"""The pirates' log is a scroll: writing adds a line, and a read shows what's new."""

from treasure_island.event_log import record_errors
from treasure_island.pirates_log import PiratesLog


def numbers(lines):
    return [line["line"] for line in lines]


def test_every_turn_a_line_a_written_note_is_a_line_saying_who_wrote_it():
    scroll = PiratesLog()
    scroll.write("pirate-1", "digging at (2, 3)")
    assert scroll.lines() == [
        {"line": 1, "text": "digging at (2, 3)", "by": "pirate-1"}
    ]


def test_every_turn_a_line_only_writing_adds_a_line():
    scroll = PiratesLog()
    scroll.write("pirate-1", "one")
    scroll.read("pirate-2")
    scroll.write("pirate-2", "two")
    assert numbers(scroll.lines()) == [1, 2]
    assert [line["text"] for line in scroll.lines()] == ["one", "two"]


def test_every_turn_a_line_a_note_stays_on_one_line():
    scroll = PiratesLog()
    scroll.write("pirate-1", "first\nsecond")
    assert scroll.lines()[0]["text"] == "first second"


def test_every_turn_a_line_lines_fit_the_event_log_format():
    scroll = PiratesLog()
    scroll.write("pirate-1", "a note")
    record = {
        "turn": 0,
        "agent": "pirate-2",
        "saw": {"position": [0, 0], "prompt": ""},
        "did": [{"action": "read"}],
        "log_shown": scroll.read("pirate-2").lines,
        "outcome": {"position": [0, 0], "found_treasure": False},
    }
    assert record_errors(record) == []


def test_reading_costs_a_read_shows_every_line_not_yet_read():
    scroll = PiratesLog()
    for number in range(1, 5):
        scroll.write("pirate-1", f"note {number}")
    answer = scroll.read("pirate-2")
    assert numbers(answer.lines) == [1, 2, 3, 4]
    assert answer.lines[0] == {"line": 1, "text": "note 1", "by": "pirate-1"}
    assert answer.message == ""


def test_reading_costs_a_second_read_shows_only_what_is_new():
    scroll = PiratesLog()
    scroll.write("pirate-1", "old")
    scroll.read("pirate-2")
    scroll.write("pirate-3", "new")
    assert scroll.read("pirate-2").lines == [
        {"line": 2, "text": "new", "by": "pirate-3"}
    ]


def test_reading_costs_each_pirate_keeps_its_own_place():
    scroll = PiratesLog()
    scroll.write("pirate-1", "old")
    scroll.read("pirate-2")
    scroll.write("pirate-1", "new")
    assert numbers(scroll.read("pirate-3").lines) == [1, 2]
    assert numbers(scroll.read("pirate-2").lines) == [2]


def test_reading_costs_a_pirate_is_not_shown_its_own_lines():
    scroll = PiratesLog()
    scroll.write("pirate-1", "mine")
    scroll.write("pirate-2", "theirs")
    scroll.write("pirate-1", "mine again")
    assert [line["text"] for line in scroll.read("pirate-1").lines] == ["theirs"]


def test_reading_costs_a_read_with_nothing_new_says_so_plainly():
    scroll = PiratesLog()
    empty = scroll.read("pirate-1")
    assert empty.lines == []
    assert "nothing" in empty.message.lower()
    scroll.write("pirate-2", "hello")
    scroll.read("pirate-1")
    again = scroll.read("pirate-1")
    assert again.lines == []
    assert "nothing new" in again.message.lower()
