# Implements: event-log/asked-or-walked, event-log/one-record-per-turn, event-log/who-acted, event-log/what-they-saw, event-log/what-they-did, event-log/what-the-log-showed, event-log/the-outcome, event-log/room-to-grow, event-log/validator
"""The validator accepts the documented format and rejects what breaks it."""

import json

import pytest

from treasure_island.event_log import log_errors, record_errors


def good_record(turn=0):
    return {
        "turn": turn,
        "agent": "pirate-a",
        "saw": {
            "position": [2, 3],
            "prompt": "You are at (2, 3).",
            "neighbours": {"north": "pirate-b"},
            "square_dug": False,
        },
        "did": [
            {"action": "move", "direction": "north"},
            {"action": "write", "text": "heading north"},
        ],
        "log_shown": [{"line": 7, "text": "pirate-b: nothing here"}],
        "outcome": {"position": [2, 2], "found_treasure": False},
    }


def changed(path, value):
    """A good record with the field at `path` replaced by `value`."""
    record = good_record()
    target = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return record


def without(path):
    record = good_record()
    target = record
    for key in path[:-1]:
        target = target[key]
    del target[path[-1]]
    return record


def write_log(tmp_path, lines):
    path = tmp_path / "events.jsonl"
    path.write_text("".join(line + "\n" for line in lines))
    return path


def test_validator_accepts_a_good_record():
    assert record_errors(good_record()) == []


def test_validator_rejects_a_bad_record_and_says_what_is_wrong():
    errors = record_errors(without(["agent"]))
    assert len(errors) == 1
    assert "agent" in errors[0]


def test_validator_rejects_a_record_that_is_not_an_object():
    assert record_errors(["not", "an", "object"])


def test_who_acted_needs_a_named_agent():
    assert record_errors(changed(["agent"], ""))
    assert record_errors(changed(["agent"], 3))


@pytest.mark.parametrize(
    "path, value",
    [
        (["saw", "position"], [2]),
        (["saw", "position"], [2, -1]),
        (["saw", "position"], [True, 3]),
        (["saw", "prompt"], None),
    ],
)
def test_what_they_saw_needs_a_position_and_a_prompt(path, value):
    assert record_errors(changed(path, value))


@pytest.mark.parametrize(
    "path, value",
    [
        (["saw", "neighbours"], ["pirate-b"]),
        (["saw", "neighbours"], {"up": "pirate-b"}),
        (["saw", "neighbours"], {"north": 3}),
        (["saw", "square_dug"], "no"),
    ],
)
def test_what_they_saw_needs_neighbours_and_whether_the_square_was_dug(path, value):
    assert record_errors(changed(path, value))
    assert record_errors(without(path))
    assert record_errors(changed(["saw", "neighbours"], {})) == []


@pytest.mark.parametrize(
    "action",
    [
        {"action": "move", "direction": "north"},
        {"action": "dig"},
        {"action": "read"},
        {"action": "enter"},
        {"action": "write", "text": ""},
        {"action": "go_to", "square": "C4"},
        {"action": "go_to", "square": "C4", "say": "Off east.", "alert": True},
        {"action": "wait", "say": "Holding here."},
        {"action": "dig", "say": "Dug C4: 3 away.", "alert": False},
        {"action": "enter", "say": "Cave at C4.", "alert": True},
    ],
)
def test_what_they_did_accepts_each_action(action):
    assert record_errors(changed(["did"], [action])) == []


def test_what_they_did_accepts_a_turn_with_no_action():
    assert record_errors(changed(["did"], [])) == []


@pytest.mark.parametrize(
    "action",
    [
        {"action": "move"},
        {"action": "move", "direction": "up"},
        {"action": "move", "direction": ["north"]},
        {"action": "write"},
        {"action": "teleport"},
        {"direction": "north"},
        "dig",
        {"action": "go_to"},
        {"action": "go_to", "square": 4},
        {"action": "wait", "say": 3},
        {"action": "dig", "alert": "yes"},
    ],
)
def test_what_they_did_rejects_a_malformed_action(action):
    assert record_errors(changed(["did"], [action]))


def test_what_they_did_must_be_a_list():
    assert record_errors(changed(["did"], {"action": "dig"}))


@pytest.mark.parametrize(
    "shown",
    [
        "pirate-b: nothing here",
        ["pirate-b: nothing here"],
        [{"line": 7}],
        [{"text": "pirate-b: nothing here"}],
    ],
)
def test_what_the_log_showed_needs_numbered_lines(shown):
    assert record_errors(changed(["log_shown"], shown))


def test_what_the_log_showed_may_say_who_wrote_each_line():
    shown = [{"line": 3, "text": "nothing here", "by": "pirate-b"}]
    assert record_errors(changed(["log_shown"], shown)) == []


def test_what_the_log_showed_can_reach_an_earlier_session():
    shown = [{"line": -1, "text": "treasure found at (4, 4)"}]
    assert record_errors(changed(["log_shown"], shown)) == []


@pytest.mark.parametrize(
    "path, value",
    [
        (["outcome", "position"], "2,2"),
        (["outcome", "found_treasure"], "no"),
        (["outcome"], None),
    ],
)
def test_the_outcome_needs_a_position_and_whether_treasure_was_found(path, value):
    assert record_errors(changed(path, value))


def test_room_to_grow_allows_extra_fields():
    record = good_record()
    record["thinking"] = "private"
    record["outcome"]["score"] = 3
    assert record_errors(record) == []


def test_one_record_per_turn_accepts_a_log_counting_up_from_zero(tmp_path):
    lines = [json.dumps(good_record(turn)) for turn in range(3)]
    assert log_errors(write_log(tmp_path, lines)) == []


@pytest.mark.parametrize("turns", [[1, 2], [0, 2], [0, 0], [1, 0]])
def test_one_record_per_turn_rejects_turns_out_of_order(tmp_path, turns):
    lines = [json.dumps(good_record(turn)) for turn in turns]
    assert log_errors(write_log(tmp_path, lines))


def test_one_record_per_turn_rejects_a_turn_that_is_not_a_number():
    assert record_errors(changed(["turn"], "0"))
    assert record_errors(changed(["turn"], True))


def test_one_record_per_turn_rejects_an_empty_log(tmp_path):
    assert log_errors(write_log(tmp_path, []))


def test_validator_names_the_line_a_log_is_wrong_on(tmp_path):
    lines = [
        json.dumps(good_record(0)),
        json.dumps({**good_record(1), "agent": ""}),
    ]
    errors = log_errors(write_log(tmp_path, lines))
    assert len(errors) == 1
    assert errors[0].startswith("line 2:")


def test_validator_reports_a_line_that_is_not_json(tmp_path):
    errors = log_errors(write_log(tmp_path, ["{not json"]))
    assert errors[0].startswith("line 1:")


def test_what_the_log_showed_says_the_turn_and_whether_it_was_an_alert():
    shown = [
        {"line": 3, "text": "Cave at C4.", "by": "pirate-b", "turn": 9, "alert": True}
    ]
    assert record_errors(changed(["log_shown"], shown)) == []


def test_asked_or_walked_a_walked_turn_says_so_and_holds_its_step():
    walked = changed(["asked"], False)
    walked["did"] = [{"action": "move", "direction": "east"}]
    walked["order"] = {"to": "E5", "arrived": False}
    walked["saw"]["prompt"] = ""
    assert record_errors(walked) == []
    asked = changed(["asked"], True)
    asked["order_ended"] = {
        "how": "blocked",
        "to": "E5",
        "at": [2, 0],
        "by": "pirate-2",
    }
    assert record_errors(asked) == []


@pytest.mark.parametrize(
    "path, value",
    [
        (["asked"], "yes"),
        (["order"], {"to": "E5"}),
        (["order"], {"to": 4, "arrived": True}),
        (["order"], "E5"),
    ],
)
def test_asked_or_walked_a_bad_order_or_asked_flag_is_rejected(path, value):
    assert record_errors(changed(path, value))
