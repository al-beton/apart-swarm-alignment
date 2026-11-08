# Implements: treasure-island/every-turn-a-line, treasure-island/shown-when-asked, treasure-island/say-on-any-action, treasure-island/alert
"""The pirates' log is a scroll: saying adds a line, and each pirate asked is shown what's new."""

from treasure_island.event_log import record_errors
from treasure_island.pirates_log import PiratesLog, line_text


def numbers(lines):
    return [line["line"] for line in lines]


def test_every_turn_a_line_a_said_line_says_who_wrote_it_on_which_turn():
    scroll = PiratesLog()
    scroll.say("pirate-1", "digging at C2", 4)
    assert scroll.lines() == [
        {
            "line": 1,
            "text": "digging at C2",
            "by": "pirate-1",
            "turn": 4,
            "alert": False,
        }
    ]


def test_every_turn_a_line_an_alert_is_marked():
    scroll = PiratesLog()
    scroll.say("pirate-2", "Cave at C4.", 9, alert=True)
    assert scroll.lines()[0]["alert"] is True
    assert line_text(scroll.lines()[0]) == "1 pirate-2 (turn 9, alert): Cave at C4."


def test_every_turn_a_line_only_saying_adds_a_line():
    scroll = PiratesLog()
    scroll.say("pirate-1", "one", 1)
    scroll.unseen("pirate-2")
    scroll.say("pirate-2", "two", 2)
    assert numbers(scroll.lines()) == [1, 2]
    assert [line["text"] for line in scroll.lines()] == ["one", "two"]


def test_every_turn_a_line_a_note_stays_on_one_line():
    scroll = PiratesLog()
    scroll.say("pirate-1", "first\nsecond", 1)
    assert scroll.lines()[0]["text"] == "first second"


def test_every_turn_a_line_lines_fit_the_event_log_format():
    scroll = PiratesLog()
    scroll.say("pirate-1", "a note", 1)
    record = {
        "turn": 1,
        "agent": "pirate-2",
        "asked": True,
        "saw": {
            "position": [0, 0],
            "prompt": "",
            "neighbours": {},
            "square_dug": False,
        },
        "did": [{"action": "wait"}],
        "log_shown": scroll.unseen("pirate-2"),
        "outcome": {"position": [0, 0], "found_treasure": False},
    }
    assert record_errors(record) == []


def test_shown_when_asked_shows_every_line_not_yet_shown():
    scroll = PiratesLog()
    for number in range(1, 5):
        scroll.say("pirate-1", f"note {number}", number)
    shown = scroll.unseen("pirate-2")
    assert numbers(shown) == [1, 2, 3, 4]
    assert shown[0]["by"] == "pirate-1"


def test_shown_when_asked_a_second_time_shows_only_what_is_new():
    scroll = PiratesLog()
    scroll.say("pirate-1", "old", 1)
    scroll.unseen("pirate-2")
    scroll.say("pirate-3", "new", 2)
    assert [line["text"] for line in scroll.unseen("pirate-2")] == ["new"]
    assert scroll.unseen("pirate-2") == []


def test_shown_when_asked_each_pirate_keeps_its_own_place():
    scroll = PiratesLog()
    scroll.say("pirate-1", "old", 1)
    scroll.unseen("pirate-2")
    scroll.say("pirate-1", "new", 2)
    assert numbers(scroll.unseen("pirate-3")) == [1, 2]
    assert numbers(scroll.unseen("pirate-2")) == [2]


def test_shown_when_asked_includes_the_pirate_s_own_lines():
    scroll = PiratesLog()
    scroll.say("pirate-1", "mine", 1)
    scroll.say("pirate-2", "theirs", 2)
    scroll.say("pirate-1", "mine again", 3)
    assert [line["text"] for line in scroll.unseen("pirate-1")] == [
        "mine",
        "theirs",
        "mine again",
    ]
