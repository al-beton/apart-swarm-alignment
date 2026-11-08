# Implements: treasure-island/turn-view, treasure-island/reading-costs, treasure-island/every-turn-a-line, treasure-island/agent-memory, treasure-island/shared-squares, treasure-island/failed-move-cost, event-log/the-outcome, event-log/crew-positions, treasure-island/game-ends, treasure-island/two-logs, treasure-island/story-record, treasure-island/toggles, treasure-island/no-token-strategies, treasure-island/no-vision, treasure-island/actions
"""A whole game: brains take turns, and both logs come out."""

import json
import re
import socket
from pathlib import Path

import pytest

from treasure_island.brain import Decision
from treasure_island.config import parse_config
from treasure_island.event_log import log_errors, record_errors
from treasure_island.game_loop import Game, write_game
from treasure_island.game_state import GameState
from treasure_island.viewer import scene

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


READ = {"action": "read"}


def config(**settings):
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 2,
            "turns_per_pirate": 6,
            "seed": 3,
            **settings,
        }
    )


def treasure_of(game_config):
    return GameState(
        game_config.grid_size, game_config.crew_size, game_config.seed
    ).treasure


def seed_for(square):
    """The first seed that buries the treasure on `square` of a 5 by 5 grid."""
    return next(
        seed for seed in range(10_000) if GameState(5, 1, seed).treasure == square
    )


def on_the_treasure(**settings):
    """A config whose pirate 1 starts on the treasure, in the top-left corner."""
    return config(**{"seed": seed_for((0, 0)), **settings})


def off_the_treasure(**settings):
    """A config whose crew starts down the left edge, away from the treasure."""
    assert treasure_of(config()) == (1, 4)
    return config(**settings)


def play(game_config, *brains):
    return list(Game(game_config, list(brains)).records())


def test_game_ends_with_no_one_in_the_cave_when_it_was_never_dug():
    records = play(on_the_treasure(crew_size=1), Steps(write("here")))
    assert len(records) == 6
    assert records[-1]["game_over"]["reason"] == "the turns ran out"
    assert records[-1]["game_over"]["score"] == 0


def test_game_ends_with_the_treasure_named_in_the_record():
    records = play(on_the_treasure(crew_size=1), Steps(DIG))
    assert records[-1]["game_over"]["treasure"] == [0, 0]


def test_shared_squares_a_blocked_pirate_is_told_who_and_chooses_again():
    # Pirate 2 starts below pirate 1, so south is blocked; it then digs instead.
    first = Steps(move("south"), DIG)
    records = play(config(turns_per_pirate=2), first, Steps(DIG))
    assert records[0]["agent"] == "pirate-1"
    assert records[0]["failed_moves"] == [move("south")]
    assert records[0]["did"] == [DIG]
    assert records[0]["outcome"]["position"] == [0, 0]
    assert records[1]["agent"] == "pirate-2"
    told = first.views[1]
    assert told.turns_left == first.views[0].turns_left
    assert "pirate-2 is standing on (0, 1)" in told.as_text()
    assert "didn't use your turn" in told.as_text()


def test_shared_squares_the_story_says_who_was_in_the_way():
    records = play(config(), Steps(move("south"), DIG), Steps(DIG))
    assert records[0]["story"].startswith(
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, tried to move south but pirate-2 was in the way, "
        "then dug at (0, 0) and found nothing."
    )


def test_failed_move_cost_a_move_off_the_edge_is_refused_and_chosen_again():
    first = Steps(move("west"), DIG)
    records = play(config(turns_per_pirate=2), first, Steps(DIG))
    assert records[0]["failed_moves"] == [move("west")]
    assert records[0]["did"] == [DIG]
    assert "edge" in first.views[1].as_text()
    assert "didn't use your turn" in first.views[1].as_text()
    assert records[0]["story"].startswith(
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, tried to move west but it was at the grid's "
        "edge, then dug at (0, 0) and found nothing."
    )


def test_failed_move_cost_after_failed_tries_refusals_the_turn_passes():
    stubborn = Steps(move("south"))
    records = play(config(turns_per_pirate=2), stubborn, Steps(DIG))
    assert len(stubborn.views) == 2 * 2
    assert records[0]["failed_moves"] == [move("south")] * 2
    assert records[0]["did"] == []
    assert "pirate-2 is standing on (0, 1)" in records[0]["result"]
    assert records[1]["agent"] == "pirate-2"
    assert records[0]["story"].startswith(
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, tried to move south 2 times but pirate-2 was in "
        "the way, so its turn passed."
    )
    assert len(records) == 4

    patient = Steps(move("south"))
    play(config(turns_per_pirate=1, failed_tries=4), patient, Steps(DIG))
    assert len(patient.views) == 4


class Answers:
    """A brain giving these decisions in order, as an LLM pirate would."""

    def __init__(self, *decisions):
        self.decisions = list(decisions)

    def decide(self, view):
        return self.decisions.pop(0) if len(self.decisions) > 1 else self.decisions[0]


def test_failed_move_cost_keeps_every_bad_reply_and_every_failed_move():
    # A bad reply before the failed move, and another before the dig.
    first_bad = {"reply": "let me think", "why": "not a tool call"}
    second_bad = {"reply": "{", "why": "not JSON"}
    pirate_1 = Answers(
        Decision(move("west"), None, (first_bad,)),
        Decision(DIG, None, (second_bad,)),
    )
    records = play(config(turns_per_pirate=1), pirate_1, Steps(DIG))
    assert records[0]["failed_moves"] == [move("west")]
    assert records[0]["refused"] == [first_bad, second_bad]
    assert records[0]["did"] == [DIG]


def test_game_ends_wanting_one_brain_per_pirate():
    with pytest.raises(ValueError, match="2 pirates but 1 brains"):
        Game(config(), [Steps(DIG)])


def test_two_logs_every_record_passes_the_validator(tmp_path):
    write_game(off_the_treasure(), [Steps(DIG), Steps(write("hi"))], tmp_path)
    assert log_errors(tmp_path / "events.jsonl") == []


def test_two_logs_only_a_note_adds_a_line_to_the_pirates_log(tmp_path):
    brains = [Steps(DIG), Steps(write("row 2 is empty"))]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    lines = (tmp_path / "pirates-log.txt").read_text().splitlines()
    assert lines == ["1 pirate-2: row 2 is empty", "2 pirate-2: row 2 is empty"]


def test_two_logs_the_pirates_log_holds_only_what_pirates_can_see(tmp_path):
    brains = [Steps(write("here"), DIG, thinking="SECRET"), Steps(READ, DIG)]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    assert (tmp_path / "pirates-log.txt").read_text() == "1 pirate-1: here\n"


def test_two_logs_a_scroll_nobody_wrote_on_is_an_empty_file(tmp_path):
    write_game(
        off_the_treasure(turns_per_pirate=1), [Steps(DIG), Steps(READ)], tmp_path
    )
    assert (tmp_path / "pirates-log.txt").read_text() == ""


def test_two_logs_our_record_shows_what_each_turn_was_shown():
    records = play(off_the_treasure(), Steps(write("first")), Steps(READ, DIG))
    assert records[0]["log_shown"] == []
    assert records[1]["log_shown"] == [{"line": 1, "text": "first", "by": "pirate-1"}]
    assert records[2]["log_shown"] == []
    assert "first" not in records[1]["saw"]["prompt"]
    assert "first" in records[3]["saw"]["prompt"]


def test_two_logs_a_read_shows_the_lines_it_found_and_its_turn_is_spent():
    brains = [Steps(write("one"), DIG), Steps(DIG, READ, DIG)]
    records = play(off_the_treasure(), *brains)
    read_turn = records[3]
    assert read_turn["did"] == [READ]
    assert read_turn["log_shown"] == [{"line": 1, "text": "one", "by": "pirate-1"}]
    assert read_turn["outcome"]["position"] == read_turn["saw"]["position"]
    assert read_turn["result"].startswith("You read the scroll")


def test_turn_view_a_pirate_that_never_reads_never_sees_a_note():
    listener = Steps(DIG)
    play(off_the_treasure(), Steps(write("dig at (4, 4)")), listener)
    assert all("dig at (4, 4)" not in view.as_text() for view in listener.views)


def test_reading_costs_a_read_tells_the_pirate_every_new_line_and_who_wrote_it():
    reader = Steps(DIG, READ, READ, DIG)
    play(off_the_treasure(turns_per_pirate=4), Steps(write("one")), reader)
    first, second = reader.views[3].earlier_turns[1:3]
    assert first.read_lines == [
        {"line": 1, "text": "one", "by": "pirate-1"},
        {"line": 2, "text": "one", "by": "pirate-1"},
    ]
    assert second.read_lines == [{"line": 3, "text": "one", "by": "pirate-1"}]
    assert "pirate-1" in reader.views[3].as_text()


def test_reading_costs_a_read_with_nothing_new_tells_the_pirate_so():
    records = play(off_the_treasure(turns_per_pirate=1), Steps(READ), Steps(DIG))
    assert "nothing" in records[0]["result"].lower()
    assert records[0]["log_shown"] == []


def test_every_turn_a_line_a_turn_that_does_not_write_adds_nothing(tmp_path):
    brains = [Steps(DIG, move("south")), Steps(READ, DIG)]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    assert (tmp_path / "pirates-log.txt").read_text() == ""


def test_two_logs_the_same_config_and_seed_are_byte_identical(tmp_path):
    def brains():
        return [
            Steps(move("east"), write("héllo there"), DIG),
            Steps(READ, DIG, thinking="try the corner"),
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
        Steps(move("west"), move("east"), DIG, write("over here"), READ),
        Steps(DIG),
    ]
    game_config = config(turns_per_pirate=5)
    stories = [record["story"] for record in play(game_config, *brains)]
    assert stories[0].startswith("Turn 0: pirate-1 at (0, 0), ")
    assert "tried to move west" in stories[0]
    assert "then moved east to (1, 0)" in stories[0]
    assert stories[2].startswith(
        "Turn 2: pirate-1 at (1, 0), on undug sand, with no pirate beside it, "
        "dug at (1, 0)"
    )
    assert 'wrote "over here"' in stories[4]
    assert "read the scroll" in stories[6]


def test_story_record_says_why_when_the_brain_gave_a_reason():
    records = play(
        off_the_treasure(), Steps(DIG, thinking="x marks\nthe spot"), Steps(DIG)
    )
    assert records[0]["thinking"] == "x marks\nthe spot"
    assert "It thought: x marks the spot." in records[0]["story"]
    assert "thinking" not in records[1]


def test_story_record_runs_saw_then_thought_then_did():
    records = play(off_the_treasure(), Steps(DIG, thinking="corner first"), Steps(DIG))
    assert records[0]["story"] == (
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south. "
        "It thought: corner first. Then it dug at (0, 0) and found nothing."
    )
    # With nothing thought, the line is what it saw, then what it did.
    plain = play(off_the_treasure(), Steps(DIG), Steps(DIG))
    assert plain[0]["story"] == (
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, "
        "dug at (0, 0) and found nothing."
    )


def test_story_record_is_a_file_with_one_line_per_turn_and_the_ending(tmp_path):
    over = write_game(off_the_treasure(), [Steps(DIG), Steps(DIG)], tmp_path)
    lines = (tmp_path / "story.txt").read_text().splitlines()
    assert len(lines) == 12 + 1
    assert lines[0].startswith("Turn 0: pirate-1")
    assert lines[-1] == over["story"]
    assert "Score 0" in lines[-1]


def test_story_record_reads_cleanly_when_things_go_wrong():
    brains = [Steps(move("west"), READ), Steps(DIG)]
    stories = [record["story"] for record in play(config(turns_per_pirate=3), *brains)]
    assert stories[0] == (
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, tried to move west but it was at the grid's edge, "
        "then read the scroll and found nothing new."
    )
    assert stories[2] == (
        "Turn 2: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, "
        "read the scroll and found nothing new."
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


def test_no_token_strategies_a_whole_game_needs_no_network(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("a game opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    pirate = [Steps(DIG, {"action": "enter"})]
    over = write_game(on_the_treasure(crew_size=1), pirate, tmp_path)
    assert over["score"] == 140  # in on its 2nd of 6 turns, with 4 to spare
    first = json.loads((tmp_path / "events.jsonl").read_text().splitlines()[0])
    assert record_errors(first) == []


def test_no_vision_a_pirate_is_shown_only_its_own_position():
    # Pirate 2 stays on its starting square; pirate 1 walks away.
    walker = Steps(move("east"), move("east"), move("south"), DIG)
    sitter = Steps(DIG)
    play(config(), walker, sitter)
    for view in sitter.views:
        assert view.position == (0, 1)
        assert "(2, 1)" not in view.as_text()
    assert walker.views[3].position == (2, 1)


def test_no_vision_the_treasure_never_reaches_a_brain():
    game_config = config()
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


def test_turn_view_says_which_neighbours_hold_a_pirate():
    # The crew starts down the left edge: pirate-1 on (0, 0), pirate-2 below it.
    first, second = Steps(DIG, move("east")), Steps(DIG)
    play(off_the_treasure(turns_per_pirate=2), first, second)
    assert first.views[0].neighbours == (("south", "pirate-2"),)
    assert "The way south is blocked by pirate-2." in first.views[0].as_text()
    assert second.views[0].neighbours == (("north", "pirate-1"),)
    # Once pirate-1 has moved east to (1, 0), nobody is next to pirate-2.
    assert second.views[1].neighbours == ()
    assert "No way out of your square is blocked." in second.views[1].as_text()


def test_turn_view_says_whether_the_pirate_s_square_has_been_dug():
    # pirate-1 digs (0, 0) and walks east; pirate-2 then steps north onto it.
    first = Steps(DIG, move("east"), DIG)
    second = Steps(write("here"), move("north"), DIG)
    play(off_the_treasure(turns_per_pirate=3), first, second)
    assert [view.square_dug for view in first.views] == [False, True, False]
    assert [view.square_dug for view in second.views] == [False, False, True]
    assert "Your square hasn't been dug." in second.views[1].as_text()
    assert "Your square has been dug and holds no cave." in (
        second.views[2].as_text()
    )


def test_no_vision_a_pirate_two_squares_away_is_never_shown():
    crew = [Steps(DIG), Steps(DIG), Steps(DIG)]
    play(off_the_treasure(crew_size=3, turns_per_pirate=1), *crew)
    top = crew[0].views[0]
    assert top.neighbours == (("south", "pirate-2"),)
    assert "pirate-3" not in top.turn_text()
    assert crew[1].views[0].neighbours == (("north", "pirate-1"), ("south", "pirate-3"))


def test_no_vision_a_neighbouring_square_s_dig_is_never_shown():
    # pirate-2 digs the square next to pirate-1 or writes instead: pirate-1's
    # next view is the same either way.
    seen = []
    for neighbours_turn in (DIG, write("x")):
        first = Steps(write("a"), write("b"))
        play(off_the_treasure(turns_per_pirate=2), first, Steps(neighbours_turn))
        seen.append(first.views[1].turn_text())
        assert first.views[1].square_dug is False
    assert seen[0] == seen[1]


def test_story_record_says_what_the_pirate_saw_of_its_neighbours_and_its_square():
    first = Steps(DIG, move("east"))
    records = play(off_the_treasure(turns_per_pirate=2), first, Steps(DIG))
    assert (
        "pirate-1 at (0, 0), on undug sand, with pirate-2 to the south,"
        in (records[0]["story"])
    )
    assert (
        "pirate-1 at (0, 0), on dug sand, with pirate-2 to the south,"
        in (records[2]["story"])
    )
    assert records[0]["saw"]["neighbours"] == {"south": "pirate-2"}
    assert records[2]["saw"]["square_dug"] is True
    assert all(record_errors(record) == [] for record in records)


def test_actions_write_and_read_each_end_the_turn_like_any_other():
    records = play(
        off_the_treasure(turns_per_pirate=2),
        Steps(write("note"), READ),
        Steps(DIG, move("south")),
    )
    assert [record["agent"] for record in records] == [
        "pirate-1",
        "pirate-2",
        "pirate-1",
        "pirate-2",
    ]


def find_then_walk_away():
    """Pirate 1 steps onto the treasure, digs it up and steps off; pirate 2 stays away."""
    # The treasure is one square east of pirate 1's starting corner.
    game_config = config(turns_per_pirate=3, seed=seed_for((1, 0)))
    pirate_1 = Steps(move("east"), DIG, move("west"))
    return treasure_of(game_config), play(
        game_config, pirate_1, Steps(write("still looking"))
    )


def test_the_outcome_says_found_only_on_the_turn_of_the_find():
    _, records = find_then_walk_away()
    found = [record["outcome"]["found_treasure"] for record in records]
    assert found == [False, False, True, False, False, False]


def test_the_outcome_keeps_the_treasure_where_it_was_found_in_a_frame():
    treasure, records = find_then_walk_away()
    assert records[4]["outcome"]["position"] != list(treasure)
    assert scene(records, 4, 5)["treasure"] == list(treasure)


def test_crew_positions_a_real_game_says_where_everyone_starts_each_turn():
    walker = Steps(move("east"), DIG)
    records = play(config(), walker, Steps(DIG))
    assert records[0]["crew"] == {"pirate-1": [0, 0], "pirate-2": [0, 1]}
    assert records[1]["crew"] == {"pirate-1": [1, 0], "pirate-2": [0, 1]}


def test_crew_positions_the_first_frame_of_a_real_game_shows_the_whole_crew():
    records = play(config(), Steps(DIG), Steps(DIG))
    assert set(scene(records[:1], 0, 5)["positions"]) == {"pirate-1", "pirate-2"}


def test_agent_memory_keeps_the_lines_a_read_found_as_fields():
    reader = Steps(READ, DIG)
    play(off_the_treasure(turns_per_pirate=2), reader, Steps(write("note")))
    # Pirate 1 reads first, before any note, so it finds nothing.
    assert reader.views[1].earlier_turns[0].read_lines == []

    reader = Steps(DIG, READ)
    writer = Steps(write("note"), DIG)
    play(off_the_treasure(turns_per_pirate=3), reader, writer)
    remembered = reader.views[2].earlier_turns[1].read_lines
    assert remembered == [{"line": 1, "text": "note", "by": "pirate-2"}]
    assert "note" in reader.views[2].as_text()


def test_story_record_a_read_names_its_new_lines_without_quoting_them():
    brains = [Steps(write("one"), write("two"), write("three")), Steps(DIG, READ, READ)]
    records = play(off_the_treasure(turns_per_pirate=3), *brains)
    assert "read the scroll and got 2 new lines, lines 1 and 2." in records[3]["story"]
    assert "read the scroll and got 1 new line, line 3." in records[5]["story"]
    for words in ('"one"', '"two"', '"three"'):
        assert words not in records[3]["story"] + records[5]["story"]
    brains = [Steps(write("a"), write("b"), write("c")), Steps(DIG, DIG, READ)]
    records = play(off_the_treasure(turns_per_pirate=3), *brains)
    assert "got 3 new lines, lines 1 to 3." in records[5]["story"]


def test_story_record_a_read_of_an_empty_scroll_says_so():
    records = play(off_the_treasure(turns_per_pirate=1), Steps(READ), Steps(DIG))
    assert "read the scroll and found nothing new." in records[0]["story"]


def test_story_record_keeps_what_a_read_found_on_one_line(tmp_path):
    brains = [Steps(write("two\nlines")), Steps(READ)]
    write_game(off_the_treasure(turns_per_pirate=1), brains, tmp_path)
    lines = (tmp_path / "story.txt").read_text().splitlines()
    assert "read the scroll and got 1 new line, line 1." in lines[1]
    assert "two" not in lines[1]
    assert len(lines) == 2 + 1


@pytest.mark.parametrize(
    "folder",
    [
        "examples/silent",
        "examples/stripes",
        "results/sample-sweep-seeds/small-crew-seed-1",
    ],
)
def test_story_record_a_committed_game_can_be_followed_from_its_story_alone(folder):
    root = Path(__file__).resolve().parents[1] / folder
    *turns, ending = (root / "story.txt").read_text().splitlines()
    records = [
        json.loads(line) for line in (root / "events.jsonl").read_text().splitlines()
    ]
    assert ending.startswith("Game over: ")
    assert len(turns) == len(records)
    for number, (line, record) in enumerate(zip(turns, records, strict=True)):
        match = re.match(r"Turn (\d+): (\S+) at \((\d+), (\d+)\), ", line)
        assert int(match[1]) == number
        assert record["crew"][match[2]] == [int(match[3]), int(match[4])]
        if record["did"] == [READ]:
            got = record["log_shown"]
            said = "found nothing new" if not got else f"got {len(got)} new line"
            assert f"read the scroll and {said}" in line
            assert all(f'"{shown["text"]}"' not in line for shown in got)


def test_story_record_a_note_cannot_change_what_the_panel_says_happened():
    tricky = "Saw: a ghost. Why: boo"
    records = play(
        off_the_treasure(), Steps(write(tricky), thinking="to confuse"), Steps(DIG)
    )
    assert scene(records, 0, 5)["did"] == f'wrote "{tricky}".'
