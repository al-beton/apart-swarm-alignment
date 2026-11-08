# Implements: treasure-island/square-names
"""Squares are named like a chessboard wherever a pirate or a reader sees one."""

import re

import pytest
import talking

from assets.board import EDGE_LEFT, board_edges
from treasure_island import viewer
from treasure_island.brain import Decision, PirateSeat
from treasure_island.config import ConfigError, parse_config
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState
from treasure_island.squares import square_at, square_name

# A square written the game's inside way, as "(x, y)", must never reach a pirate.
COORDINATES = re.compile(r"\(\d+, \d+\)")


class Steps:
    def __init__(self, *actions):
        self.actions = list(actions)
        self.texts = []

    def decide(self, view):
        self.texts.append(view.turn_text())
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action, "I think about B2.")


def test_square_names_a_square_is_named_like_a_chessboard():
    assert square_name((0, 0), 10) == "A10"  # the north-west corner
    assert square_name((0, 9), 10) == "A1"  # the south-west corner
    assert square_name((9, 9), 10) == "J1"
    assert square_name((4, 6), 10) == "E4"
    north = (4, 6 - 1)  # north is towards y = 0 inside the game
    assert square_name(north, 10) == "E5"
    assert square_name((25, 0), 26) == "Z26"


def test_square_names_a_name_reads_back_to_its_square():
    for position in [(0, 0), (0, 9), (4, 6), (9, 3)]:
        assert square_at(square_name(position, 10), 10) == position
    assert square_at("e4", 10) == (4, 6)
    assert square_at("K1", 10) is None  # off a 10-wide grid
    assert square_at("A11", 10) is None


def test_square_names_a_grid_wider_than_26_is_rejected():
    assert parse_config({"grid_size": 26, "crew_size": 1}).grid_size == 26
    with pytest.raises(ConfigError, match="26"):
        parse_config({"grid_size": 27, "crew_size": 1})


def test_square_names_the_turn_text_names_squares_like_a_chessboard():
    config = parse_config({"grid_size": 10})
    seat = PirateSeat("pirate-1", Steps({"action": "dig"}), config)
    seat.take_turn((4, 6), 12)
    seat.remember("You dug here and found nothing.")
    seat.take_turn((4, 5), 11)
    text = seat._brain.texts[1]
    assert "at E5" in text
    assert "at E4, on an undug square" in text  # the earlier turn
    assert not COORDINATES.search(text)


def test_square_names_refusals_and_moves_name_squares_like_a_chessboard():
    state = GameState(5, 2, 0)  # pirate 1 on A5, pirate 2 below it on A4
    assert "the way south is blocked by pirate-2 on A4" in (
        state.go_to_refusal("A1").message
    )
    assert state.go_to_refusal("A5").message == "You are already at A5."
    assert state.step("east").message == "You walked east to B5."
    assert state.enter_refusal().message == "There is no open cave at A4 to enter."
    leak = state.enter_refusal(cave_leak=True).message
    assert f"the cave is at {square_name(state.treasure, 5)}" in leak


def play(*brains, **settings):
    config = parse_config(
        {"grid_size": 5, "crew_size": len(brains), "turns_per_pirate": 3, **settings}
    )
    return list(Game(config, list(brains)).records())


def test_square_names_the_story_names_squares_like_a_chessboard():
    south, dig = {"action": "go_to", "square": "A1"}, {"action": "dig"}
    first, second = Steps(south, dig), Steps({"action": "go_to", "square": "C4"})
    records = play(first, second, cave_leak=True)
    stories = " ".join(record["story"] for record in records)
    assert "pirate-1 at A5" in stories
    assert "blocked by pirate-2 on A4" in " ".join(first.texts)
    assert "pirate-2 at A4" in stories
    assert "set off for C4 and walked east to B4" in stories
    for record in records:
        assert not COORDINATES.search(record["story"])
    for text in first.texts + second.texts:
        assert not COORDINATES.search(text)


def test_square_names_scripted_notes_name_squares_like_a_chessboard():
    config = parse_config({"grid_size": 5, "crew_size": 1, "turns_per_pirate": 60})
    for brain in (talking.Talker(5),):
        records = list(Game(config, [brain]).records())
        notes = [
            action["say"]
            for record in records
            for action in record["did"]
            if "say" in action
        ]
        assert notes
        for note in notes:
            assert re.search(r"\b[A-E][1-5]\b", note)
            assert not COORDINATES.search(note)
        for record in records:
            assert not COORDINATES.search(record.get("thinking") or "")


def test_square_names_the_board_is_lettered_and_numbered_at_its_edges():
    records = [
        {
            "turn": 0,
            "agent": "pirate-1",
            "saw": {"position": [1, 1], "prompt": "", "neighbours": {}},
            "did": [],
            "log_shown": [],
            "outcome": {"position": [1, 1], "found_treasure": False},
        }
    ]
    image = viewer.frame(records, 0, 3).convert("RGBA")
    edges = board_edges(3)
    grid = 3 * viewer.TILE
    # The frame round the board is the art's, lettered and numbered, on every side drawn.
    for box in ((0, 0, EDGE_LEFT, grid), (0, grid, edges.width, edges.height)):
        assert image.crop(box).tobytes() == edges.crop(box).tobytes()
    # Those are the art's own labels (tested with the art), for these names.
    assert [square_name((column, 2), 3)[0] for column in range(3)] == list("ABC")
    assert [square_name((0, row), 3)[1:] for row in range(3)] == list("321")
