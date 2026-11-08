"""The event-log format: one JSON object per turn, and its validator.

The format is documented in product/spec/event-log.md. Only required fields are
checked, so a record may carry more (event-log/room-to-grow).

Implements: treasure-island/share-reading, treasure-island/leak-form, event-log/asked-or-walked, event-log/one-record-per-turn, event-log/who-acted, event-log/what-they-saw, event-log/what-they-did, event-log/what-the-log-showed, event-log/the-outcome, event-log/room-to-grow, event-log/validator
"""

import json

DIRECTIONS = ("north", "east", "south", "west")


def _is_int(value):
    # bool is a subclass of int, but `true` is not a turn or a line number.
    return isinstance(value, int) and not isinstance(value, bool)


def _is_text(value):
    return isinstance(value, str)


def _is_position(value):
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(_is_int(n) and n >= 0 for n in value)
    )


def _is_log_line(value):
    return (
        isinstance(value, dict)
        and _is_int(value.get("line"))
        and _is_text(value.get("text"))
    )


def _talks(action):
    """An action's optional line to say and alert flag, if it has them, are sound.

    Only a dig can share its reading, so any other action with `share` is wrong.
    """
    return (
        _is_text(action.get("say", ""))
        and isinstance(action.get("alert", False), bool)
        and "share" not in action
    )


def _digs(action):
    """A dig's line and alert are sound, and `share`, when there, is true."""
    rest = {key: value for key, value in action.items() if key != "share"}
    return _talks(rest) and action.get("share", True) is True


# Each action's name, and the check on what else that action must say. The v2
# tool calls are go_to, dig, wait and enter, each of which may say a line; a
# `move` is one step, the game's own under an order. `read` and `write` (and a
# `move` a pirate chose) are first-rules actions, kept so archived games still
# pass the validator.
_ACTIONS = {
    "go_to": lambda action: _is_text(action.get("square")) and _talks(action),
    "move": lambda action: action.get("direction") in DIRECTIONS,
    "dig": _digs,
    "wait": _talks,
    "enter": _talks,
    "survey": lambda action: set(action) == {"action"},  # the leak's tool form
    "read": lambda action: True,
    "write": lambda action: _is_text(action.get("text")),
}


def is_action(value):
    if not isinstance(value, dict) or not _is_text(value.get("action")):
        return False
    check = _ACTIONS.get(value["action"])
    return check is not None and check(value)


def _did_errors(did):
    if not isinstance(did, list):
        return ["did must be a list of actions"]
    return [
        f"did[{i}] is not a valid action: {json.dumps(action)}"
        for i, action in enumerate(did)
        if not is_action(action)
    ]


def _shared_errors(shared):
    """A dig's shared reading names its scroll `line`, its `square` and `away`."""
    if shared is None:
        return []
    if not (
        isinstance(shared, dict)
        and _is_int(shared.get("line"))
        and _is_text(shared.get("square"))
        and _is_int(shared.get("away"))
    ):
        return ["shared must name the scroll `line`, the `square` and the `away`"]
    return []


def _asked_errors(record):
    """`asked`, where a record has it, says whether the pirate's brain was asked."""
    if "asked" in record and not isinstance(record["asked"], bool):
        return ["asked must be true or false"]
    order = record.get("order")
    if order is not None and not (
        isinstance(order, dict)
        and _is_text(order.get("to"))
        and isinstance(order.get("arrived"), bool)
    ):
        return ["order must name the square it is `to` and whether it `arrived`"]
    errors = _order_ended_errors(record.get("order_ended"))
    if record.get("asked") is False:
        # A walked turn's brain was shown nothing (first-rules records have no
        # `asked`, so they are never held to this).
        saw = record.get("saw")
        if isinstance(saw, dict) and saw.get("prompt") != "":
            errors.append("a walked turn (asked: false) must have an empty saw.prompt")
        if record.get("log_shown") != []:
            errors.append("a walked turn (asked: false) must have an empty log_shown")
    return errors


ORDER_ENDS = ("arrived", "blocked", "alert")


def _order_ended_errors(ended):
    """What is wrong with an `order_ended`: how, to, at, and by when blocked."""
    if ended is None:
        return []
    if not (
        isinstance(ended, dict)
        and ended.get("how") in ORDER_ENDS
        and _is_text(ended.get("to"))
        and _is_position(ended.get("at"))
        and _is_text(ended.get("by", ""))
        and (ended["how"] != "blocked" or ended.get("by"))
    ):
        why = (
            "order_ended must say `how` it ended (arrived, blocked or alert), the "
            "square it was going `to`, where it stopped `at` and, when blocked, "
            "`by` whom"
        )
        return [why]
    return []


def _log_shown_errors(shown):
    if not isinstance(shown, list):
        return ["log_shown must be a list of log lines"]
    return [
        f"log_shown[{i}] needs a line number and text"
        for i, line in enumerate(shown)
        if not _is_log_line(line)
    ]


def _position_errors(section, record):
    part = record.get(section)
    if not isinstance(part, dict):
        return [f"{section} must be an object"]
    if not _is_position(part.get("position")):
        return [f"{section}.position must be [x, y] with x and y at least 0"]
    return []


def _surroundings_errors(saw):
    """What's wrong with what a record says the pirate saw around it."""
    if not isinstance(saw, dict):
        return []
    errors = []
    neighbours = saw.get("neighbours")
    if not isinstance(neighbours, dict) or not all(
        direction in DIRECTIONS and _is_text(name) and name
        for direction, name in neighbours.items()
    ):
        errors.append(
            "saw.neighbours must map each direction that holds a pirate to its name"
        )
    if not isinstance(saw.get("square_dug"), bool):
        errors.append("saw.square_dug must say whether the pirate's square was dug")
    return errors


def record_errors(record):
    """What is wrong with one record, as a list of messages (empty if valid)."""
    if not isinstance(record, dict):
        return ["a record must be a JSON object"]
    errors = []
    turn = record.get("turn")
    if not _is_int(turn) or turn < 0:
        errors.append("turn must be a whole number from 0")
    agent = record.get("agent")
    if not _is_text(agent) or not agent:
        errors.append("agent must name the pirate that took the turn")
    errors += _position_errors("saw", record)
    if isinstance(record.get("saw"), dict) and not _is_text(
        record["saw"].get("prompt")
    ):
        errors.append("saw.prompt must be the text the pirate was given")
    errors += _surroundings_errors(record.get("saw"))
    errors += _did_errors(record.get("did"))
    errors += _shared_errors(record.get("shared"))
    errors += _asked_errors(record)
    errors += _log_shown_errors(record.get("log_shown"))
    errors += _position_errors("outcome", record)
    outcome = record.get("outcome")
    if isinstance(outcome, dict) and not isinstance(
        outcome.get("found_treasure"), bool
    ):
        errors.append("outcome.found_treasure must be true or false")
    return errors


def _line_errors(text, expected_turn):
    try:
        record = json.loads(text)
    except json.JSONDecodeError as error:
        return [f"not JSON: {error}"]
    errors = record_errors(record)
    if not errors and record["turn"] != expected_turn:
        errors = [f"turn is {record['turn']}, expected {expected_turn}"]
    return errors


def log_errors(path):
    """What is wrong with a whole log file, each message naming its line."""
    with open(path, encoding="utf-8") as log:
        lines = log.read().splitlines()
    if not lines:
        return ["the log has no records"]
    return [
        f"line {number}: {error}"
        for number, text in enumerate(lines, start=1)
        for error in _line_errors(text, expected_turn=number - 1)
    ]
