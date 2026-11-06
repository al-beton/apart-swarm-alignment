# Implements: runs/walking-skeleton
"""The tiny game that proves the path from config to events."""

import pytest

from treasure_island.backends import UnknownModel, backend_for
from treasure_island.game import Config, play


def asking(*replies):
    """An `ask` that gives these replies in order, then repeats the last."""
    queue = list(replies)
    return lambda request: queue.pop(0) if len(queue) > 1 else queue[0]


def solo(**settings):
    """A one-pirate game with the grid so small the treasure must be underfoot."""
    return Config(**{"size": 1, "pirates": 1, "turns": 5, **settings})


def test_walking_skeleton_digging_on_the_treasure_ends_the_game():
    events = list(play(solo(), 0, asking("dig")))
    assert len(events) == 1
    assert events[0]["did"] == [{"action": "dig"}]
    assert events[0]["outcome"]["found_treasure"] is True


def test_walking_skeleton_a_pirate_stays_on_the_grid():
    events = list(play(solo(), 0, asking("move west", "move north", "dig")))
    assert [event["outcome"]["position"] for event in events] == [[0, 0]] * 3


def test_walking_skeleton_a_reply_it_cannot_read_is_a_turn_with_no_action():
    event = next(play(solo(), 0, asking("I would rather not")))
    assert event["did"] == []
    assert event["outcome"]["found_treasure"] is False


def test_walking_skeleton_the_game_stops_at_the_turn_limit():
    events = list(play(Config(size=3, pirates=2, turns=7), 0, asking("wait")))
    assert [event["turn"] for event in events] == list(range(7))
    assert [event["agent"] for event in events[:3]] == [
        "pirate-a",
        "pirate-b",
        "pirate-a",
    ]


def test_walking_skeleton_an_unknown_model_is_refused():
    with pytest.raises(UnknownModel):
        backend_for("some-provider/some-model")
