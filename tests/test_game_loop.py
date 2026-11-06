# Implements: treasure-island/game-ends, treasure-island/two-logs, treasure-island/story-record, treasure-island/toggles, treasure-island/no-token-strategies, treasure-island/no-vision, treasure-island/actions
"""A whole game: brains take turns, and both logs come out."""

import json
import socket

import pytest

from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.event_log import log_errors, record_errors
from treasure_island.game_loop import Game, write_game
from treasure_island.game_state import GameState

DIG = {"action": "dig"}


class Steps:
    """A strategy: these actions in order, then the last one for ever."""

    def __init__(self, *actions, thinking=None):
        self.actions = list(actions)
        self.thinking = thinking
        self.views = []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action, self.thinking)


def move(direction):
    return {"action": "move", "direction": direction}


def write(text):
    return {"action": "write", "text": text}


def read(line):
    return {"action": "read", "line": line}


def config(**settings):
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 2,
            "turns_per_pirate": 6,
            "seed": 3,
            "landing_square": [0, 0],
            **settings,
        }
    )


def treasure_of(game_config):
    return GameState(
        game_config.grid_size,
        game_config.crew_size,
        game_config.landing_square,
        game_config.seed,
    ).treasure


def on_the_treasure(**settings):
    """A config whose crew lands right on the treasure."""
    return config(**{**settings, "landing_square": list(treasure_of(config()))})


def off_the_treasure(**settings):
    x, y = treasure_of(config())
    landing = [(x + 1) % 5, y]
    return config(**{**settings, "landing_square": landing})


def play(game_config, *brains):
    return list(Game(game_config, list(brains)).records())


def test_game_ends_when_everyone_is_on_the_dug_up_treasure():
    records = play(on_the_treasure(), Steps(DIG), Steps(DIG))
    assert len(records) == 1
    assert records[0]["game_over"]["reason"] == "everyone is on the treasure"
    # Pirate 1 dug on its first of 6 turns, leaving it 5.
    assert records[0]["game_over"]["moves_remaining"] == 5
    assert records[0]["game_over"]["score"] == 150


def test_game_ends_counting_the_moves_of_the_pirate_who_got_there_last():
    x, y = treasure_of(config())
    landing = [x, (y + 1) % 5] if y < 4 else [x, y - 1]
    step = "north" if y < 4 else "south"
    game_config = config(landing_square=landing)
    # Pirate 2 steps on and digs: its 2nd turn ends the game, leaving it 4.
    records = play(game_config, Steps(move(step), DIG), Steps(move(step), DIG))
    assert records[-1]["game_over"]["moves_remaining"] == 4
    assert records[-1]["game_over"]["score"] == 140


def test_game_ends_when_the_turns_run_out():
    records = play(off_the_treasure(), Steps(DIG), Steps(DIG))
    assert len(records) == 2 * 6
    assert "game_over" not in records[-2]
    assert records[-1]["game_over"]["reason"] == "the turns ran out"
    assert records[-1]["game_over"]["score"] == 10


def test_game_ends_only_if_the_treasure_has_been_dug_up():
    records = play(on_the_treasure(), Steps(write("here")), Steps(write("me too")))
    assert len(records) == 12
    assert records[-1]["game_over"]["reason"] == "the turns ran out"
    assert records[-1]["game_over"]["score"] == 10


def test_game_ends_with_the_treasure_named_in_the_record():
    records = play(on_the_treasure(), Steps(DIG), Steps(DIG))
    assert records[-1]["game_over"]["treasure"] == list(treasure_of(config()))


def test_game_ends_wanting_one_brain_per_pirate():
    with pytest.raises(ValueError, match="2 pirates but 1 brains"):
        Game(config(), [Steps(DIG)])


def test_two_logs_every_record_passes_the_validator(tmp_path):
    write_game(off_the_treasure(), [Steps(DIG), Steps(write("hi"))], tmp_path)
    assert log_errors(tmp_path / "events.jsonl") == []


def test_two_logs_every_turn_adds_one_line_to_the_pirates_log(tmp_path):
    brains = [Steps(DIG), Steps(write("row 2 is empty"))]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    lines = (tmp_path / "pirates-log.txt").read_text().splitlines()
    assert lines == ["1:", "2: row 2 is empty", "3:", "4: row 2 is empty"]


def test_two_logs_the_pirates_log_holds_only_what_pirates_can_see(tmp_path):
    brains = [Steps(move("south"), DIG), Steps(read(1), move("east"), DIG)]
    write_game(on_the_treasure(), brains, tmp_path)
    text = (tmp_path / "pirates-log.txt").read_text()
    assert [line.split(":", 1)[1] for line in text.splitlines()] == [""] * len(
        text.splitlines()
    )


def test_two_logs_our_record_shows_what_each_turn_was_shown():
    records = play(off_the_treasure(), Steps(write("first")), Steps(read(1), DIG))
    assert records[0]["log_shown"] == []
    assert records[1]["log_shown"][0] == {"line": 1, "text": "first"}
    assert records[1]["saw"]["prompt"].count("first") >= 1


def test_two_logs_a_read_shows_the_lines_it_found_and_its_turn_is_spent():
    game_config = off_the_treasure(log_window=1, read_size=1)
    brains = [Steps(write("one"), DIG), Steps(DIG, read(1), DIG)]
    records = play(game_config, *brains)
    read_turn = records[3]
    assert read_turn["did"] == [read(1)]
    assert {"line": 1, "text": "one"} in read_turn["log_shown"]
    assert read_turn["outcome"]["position"] == read_turn["saw"]["position"]
    assert read_turn["result"].startswith("You read the log")


def test_two_logs_the_same_config_and_seed_are_byte_identical(tmp_path):
    def brains():
        return [
            Steps(move("east"), write("héllo there"), DIG),
            Steps(read(1), DIG, thinking="try the corner"),
        ]

    for name in ("a", "b"):
        (tmp_path / name).mkdir()
        write_game(off_the_treasure(), brains(), tmp_path / name)
    for file in ("events.jsonl", "pirates-log.txt", "story.txt"):
        assert (tmp_path / "a" / file).read_bytes() == (
            tmp_path / "b" / file
        ).read_bytes()


def test_story_record_says_who_did_what_in_plain_words():
    brains = [
        Steps(move("west"), move("east"), DIG, write("over here"), read(1)),
        Steps(DIG),
    ]
    game_config = config(turns_per_pirate=5, landing_square=[0, 0], seed=3)
    stories = [record["story"] for record in play(game_config, *brains)]
    assert stories[0].startswith("Turn 0: pirate-1 at (0, 0) ")
    assert "tried to move west" in stories[0]
    assert stories[2].startswith("Turn 2: pirate-1 at (0, 0) moved east to (1, 0)")
    assert "dug at (1, 0)" in stories[4]
    assert 'wrote "over here"' in stories[6]
    assert "read the log around line 1" in stories[8]


def test_story_record_says_why_when_the_brain_gave_a_reason():
    records = play(
        off_the_treasure(), Steps(DIG, thinking="x marks\nthe spot"), Steps(DIG)
    )
    assert records[0]["thinking"] == "x marks\nthe spot"
    assert records[0]["story"].endswith("Why: x marks the spot")
    assert "thinking" not in records[1]


def test_story_record_is_a_file_with_one_line_per_turn_and_the_ending(tmp_path):
    over = write_game(off_the_treasure(), [Steps(DIG), Steps(DIG)], tmp_path)
    lines = (tmp_path / "story.txt").read_text().splitlines()
    assert len(lines) == 12 + 1
    assert lines[0].startswith("Turn 0: pirate-1")
    assert lines[-1] == over["story"]
    assert "Score 10" in lines[-1]


def test_story_record_reads_cleanly_when_things_go_wrong():
    brains = [Steps(move("west"), read(99)), Steps(DIG)]
    stories = [
        record["story"]
        for record in play(config(turns_per_pirate=3, landing_square=[0, 0]), *brains)
    ]
    assert stories[0] == "Turn 0: pirate-1 at (0, 0) tried to move west and couldn't."
    assert stories[2] == (
        "Turn 2: pirate-1 at (0, 0) read the log around line 99 and found nothing there."
    )


def test_story_record_keeps_a_note_on_one_line(tmp_path):
    brains = [Steps(write("two\nlines")), Steps(DIG)]
    write_game(off_the_treasure(turns_per_pirate=1), brains, tmp_path)
    lines = (tmp_path / "story.txt").read_text().splitlines()
    assert 'wrote "two lines"' in lines[0]
    assert len(lines) == 2 + 1


def test_toggles_the_crew_size_changes_through_the_config_alone():
    three = [Steps(DIG) for _ in range(3)]
    records = play(off_the_treasure(crew_size=3, turns_per_pirate=1), *three)
    assert [record["agent"] for record in records] == [
        "pirate-1",
        "pirate-2",
        "pirate-3",
    ]


@pytest.mark.parametrize("window", [0, 1, 4])
def test_toggles_the_log_length_changes_through_the_config_alone(window):
    game_config = off_the_treasure(log_window=window, turns_per_pirate=5)
    records = play(game_config, Steps(write("note")), Steps(write("note")))
    assert len(records[-1]["log_shown"]) == window


def test_no_token_strategies_a_whole_game_needs_no_network(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("a game opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    over = write_game(on_the_treasure(), [Steps(DIG), Steps(DIG)], tmp_path)
    assert over["score"] == 150
    first = json.loads((tmp_path / "events.jsonl").read_text().splitlines()[0])
    assert record_errors(first) == []


def test_no_vision_a_pirate_is_shown_only_its_own_position():
    # Pirate 2 stays on the landing square; pirate 1 walks away from it.
    walker = Steps(move("east"), move("east"), move("south"), DIG)
    sitter = Steps(DIG)
    play(config(landing_square=[0, 0]), walker, sitter)
    for view in sitter.views:
        assert view.position == (0, 0)
        assert "(2, 1)" not in view.as_text()
    assert walker.views[3].position == (2, 1)


def test_no_vision_the_treasure_never_reaches_a_brain():
    game_config = config(landing_square=[0, 0], seed=3)
    x, y = treasure_of(game_config)
    brain = Steps(DIG)
    play(game_config, brain, Steps(DIG))
    assert (x, y) != (0, 0)
    for view in brain.views:
        assert f"({x}, {y})" not in view.as_text()


def test_no_vision_a_dig_result_reaches_only_the_digger():
    brains = [Steps(DIG), Steps(write("nothing to report"))]
    records = play(off_the_treasure(turns_per_pirate=2), *brains)
    assert "You dug here" in brains[0].views[1].as_text()
    assert "You dug here" not in brains[1].views[1].as_text()
    assert records[-1]["agent"] == "pirate-2"


def test_actions_write_and_read_each_end_the_turn_like_any_other():
    records = play(
        off_the_treasure(turns_per_pirate=2),
        Steps(write("note"), read(1)),
        Steps(DIG, move("south")),
    )
    assert [record["agent"] for record in records] == [
        "pirate-1",
        "pirate-2",
        "pirate-1",
        "pirate-2",
    ]
