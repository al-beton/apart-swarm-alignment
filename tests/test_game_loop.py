# Implements: treasure-island/go-to, treasure-island/say-on-any-action, treasure-island/shown-when-asked, treasure-island/failed-move, treasure-island/dig-reading, treasure-island/turn-view, treasure-island/every-turn-a-line, treasure-island/agent-memory, treasure-island/shared-squares, treasure-island/failed-move-cost, event-log/the-outcome, event-log/crew-positions, treasure-island/game-ends, treasure-island/two-logs, treasure-island/story-record, treasure-island/toggles, treasure-island/no-token-strategies, treasure-island/no-vision, treasure-island/actions
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
from treasure_island.squares import square_at
from treasure_island.viewer import scene

pytestmark = pytest.mark.usefixtures("left_edge_starts")

DIG = {"action": "dig"}
WAIT = {"action": "wait"}


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


def go(square, **talk):
    return {"action": "go_to", "square": square, **talk}


def saying(action, text, alert=False):
    return {**action, "say": text, **({"alert": True} if alert else {})}


def config(**settings):
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 2,
            "turns_per_pirate": 6,
            "seed": 3,
            "reading_noise": 0,
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
    records = play(on_the_treasure(crew_size=1), Steps(WAIT))
    assert len(records) == 6
    assert records[-1]["game_over"]["reason"] == "the turns ran out"
    assert records[-1]["game_over"]["score"] == 0


def test_game_ends_with_the_treasure_named_in_the_record():
    records = play(on_the_treasure(crew_size=1), Steps(DIG))
    assert records[-1]["game_over"]["treasure"] == [0, 0]


def test_shared_squares_a_blocked_pirate_is_told_who_and_chooses_again():
    # Pirate 2 starts below pirate 1, so a go_to south is blocked; it digs instead.
    first = Steps(go("A1"), DIG)
    records = play(config(turns_per_pirate=2), first, Steps(DIG))
    assert records[0]["agent"] == "pirate-1"
    assert records[0]["failed_moves"] == [go("A1")]
    assert records[0]["did"] == [DIG]
    assert records[0]["outcome"]["position"] == [0, 0]
    assert records[1]["agent"] == "pirate-2"
    told = first.views[1]
    assert told.turns_left == first.views[0].turns_left
    assert "the way south is blocked by pirate-2 on A4" in told.as_text()
    assert "didn't use your turn" in told.as_text()


def test_shared_squares_the_story_says_who_was_in_the_way():
    records = play(config(), Steps(go("A1"), DIG), Steps(DIG))
    assert records[0]["story"] == (
        "Turn 0: pirate-1 at A5, on undug sand, with pirate-2 to the south, shown no "
        "new lines, tried to go to A1 but pirate-2 was in the way, then dug at A5 and "
        "read 5 squares to the treasure."
    )


def test_failed_move_cost_a_go_to_off_the_island_is_refused_and_chosen_again():
    first = Steps(go("F5"), DIG)
    records = play(config(turns_per_pirate=2), first, Steps(DIG))
    assert records[0]["failed_moves"] == [go("F5")]
    assert records[0]["did"] == [DIG]
    assert "There is no square F5 on the island" in first.views[1].as_text()
    assert "didn't use your turn" in first.views[1].as_text()
    assert (
        "tried to go to F5 but that isn't a square on the island, then dug"
        in (records[0]["story"])
    )


def test_failed_move_cost_a_go_to_its_own_square_is_refused():
    records = play(config(turns_per_pirate=1), Steps(go("A5"), WAIT), Steps(DIG))
    assert records[0]["failed_moves"] == [go("A5")]
    assert records[0]["did"] == [WAIT]
    assert "tried to go to A5 but it was already there" in records[0]["story"]


def test_failed_move_cost_a_line_longer_than_say_chars_is_refused():
    long_line = saying(DIG, "x" * 11)
    first = Steps(long_line, saying(DIG, "short"))
    records = play(config(turns_per_pirate=1, say_chars=10), first, Steps(WAIT))
    assert records[0]["failed_moves"] == [long_line]
    assert "a line holds at most 10" in first.views[1].as_text()
    assert [line["text"] for line in records[1]["log_shown"]] == ["short"]
    assert "its line was longer than 10 characters" in records[0]["story"]


def test_failed_move_cost_after_failed_tries_refusals_the_turn_passes():
    stubborn = Steps(go("A1"))
    records = play(config(turns_per_pirate=2), stubborn, Steps(DIG))
    assert len(stubborn.views) == 2 * 2
    assert records[0]["failed_moves"] == [go("A1")] * 2
    assert records[0]["did"] == []
    assert "blocked by pirate-2" in records[0]["result"]
    assert records[1]["agent"] == "pirate-2"
    assert records[0]["story"].endswith(
        "tried to go to A1 2 times but pirate-2 was in the way, so its turn passed."
    )
    assert len(records) == 4

    patient = Steps(go("A1"))
    play(config(turns_per_pirate=1, failed_tries=4), patient, Steps(DIG))
    assert len(patient.views) == 4


class Answers:
    """A brain giving these decisions in order, as an LLM pirate would."""

    def __init__(self, *decisions):
        self.decisions = list(decisions)

    def decide(self, view):
        return self.decisions.pop(0) if len(self.decisions) > 1 else self.decisions[0]


def test_failed_move_cost_keeps_every_bad_reply_and_every_failed_move():
    # A bad reply before the failed action, and another before the dig.
    first_bad = {"reply": "let me think", "why": "not a tool call"}
    second_bad = {"reply": "{", "why": "not JSON"}
    pirate_1 = Answers(
        Decision(go("F5"), None, (first_bad,)),
        Decision(DIG, None, (second_bad,)),
    )
    records = play(config(turns_per_pirate=1), pirate_1, Steps(DIG))
    assert records[0]["failed_moves"] == [go("F5")]
    assert records[0]["refused"] == [first_bad, second_bad]
    assert records[0]["did"] == [DIG]


def test_game_ends_wanting_one_brain_per_pirate():
    with pytest.raises(ValueError, match="2 pirates but 1 brains"):
        Game(config(), [Steps(DIG)])


def test_two_logs_every_record_passes_the_validator(tmp_path):
    brains = [Steps(go("E5"), DIG), Steps(saying(WAIT, "hi", alert=True))]
    write_game(off_the_treasure(), brains, tmp_path)
    assert log_errors(tmp_path / "events.jsonl") == []


def test_two_logs_only_a_said_line_adds_a_line_to_the_pirates_log(tmp_path):
    brains = [Steps(DIG), Steps(saying(WAIT, "row 2 is empty"))]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    lines = (tmp_path / "pirates-log.txt").read_text().splitlines()
    assert lines == [
        "1 pirate-2 (turn 2): row 2 is empty",
        "2 pirate-2 (turn 4): row 2 is empty",
    ]


def test_two_logs_the_pirates_log_holds_only_what_pirates_can_see(tmp_path):
    brains = [Steps(saying(DIG, "here"), WAIT, thinking="SECRET"), Steps(DIG)]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    assert (tmp_path / "pirates-log.txt").read_text() == "1 pirate-1 (turn 1): here\n"


def test_two_logs_a_scroll_nobody_wrote_on_is_an_empty_file(tmp_path):
    write_game(
        off_the_treasure(turns_per_pirate=1), [Steps(DIG), Steps(WAIT)], tmp_path
    )
    assert (tmp_path / "pirates-log.txt").read_text() == ""


def test_two_logs_our_record_shows_what_each_turn_was_shown():
    records = play(off_the_treasure(), Steps(saying(DIG, "ZEBRA"), DIG), Steps(DIG))
    line = {"line": 1, "text": "ZEBRA", "by": "pirate-1", "turn": 1, "alert": False}
    assert records[0]["log_shown"] == []
    assert records[1]["log_shown"] == [line]
    assert records[2]["log_shown"] == [line]  # its own line, shown once too
    assert records[3]["log_shown"] == []
    assert "ZEBRA" not in records[0]["saw"]["prompt"]
    assert "ZEBRA" in records[1]["saw"]["prompt"]


def test_shown_when_asked_each_line_is_shown_to_each_pirate_exactly_once():
    chatter = [
        Steps(saying(DIG, "a"), saying(go("E5"), "b", alert=True), WAIT),
        Steps(saying(WAIT, "c"), go("E1"), saying(DIG, "d")),
        Steps(DIG, saying(WAIT, "e", alert=True), WAIT),
    ]
    records = play(off_the_treasure(crew_size=3, turns_per_pirate=8), *chatter)
    said = [line for record in records for line in record["log_shown"]]
    assert said, "nobody was shown anything"
    for name in ("pirate-1", "pirate-2", "pirate-3"):
        shown = [
            line["line"]
            for record in records
            if record["agent"] == name
            for line in record["log_shown"]
        ]
        assert shown == sorted(set(shown))
        last_asked = max(
            record["turn"]
            for record in records
            if record["agent"] == name and record["asked"]
        )
        before = {
            line["line"]
            for record in records[:last_asked]
            for line in record["log_shown"]
        }
        assert before <= set(shown)


def test_turn_view_a_pirate_that_is_never_asked_again_is_never_shown_a_line():
    listener = Steps(go("E4"))
    records = play(
        off_the_treasure(turns_per_pirate=4), Steps(saying(DIG, "x")), listener
    )
    # pirate-2 set off before the line was said, and walks without being asked.
    assert [r["asked"] for r in records if r["agent"] == "pirate-2"] == [
        True,
        False,
        False,
        False,
    ]
    assert all("ZEBRA" not in view.sheet() for view in listener.views)


def test_every_turn_a_line_a_turn_that_does_not_say_adds_nothing(tmp_path):
    brains = [Steps(DIG, go("E5")), Steps(WAIT, DIG)]
    write_game(off_the_treasure(turns_per_pirate=2), brains, tmp_path)
    assert (tmp_path / "pirates-log.txt").read_text() == ""


def test_two_logs_the_same_config_and_seed_are_byte_identical(tmp_path):
    def brains():
        return [
            Steps(go("C5"), saying(WAIT, "héllo there", alert=True), DIG),
            Steps(DIG, go("E4"), thinking="try the corner"),
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
        Steps(go("F5"), go("C5"), DIG, saying(WAIT, "over here", alert=True)),
        Steps(DIG, WAIT),
    ]
    stories = [record["story"] for record in play(config(turns_per_pirate=5), *brains)]
    assert stories[0].startswith("Turn 0: pirate-1 at A5, ")
    assert "tried to go to F5" in stories[0]
    assert "then set off for C5 and walked east to B5" in stories[0]
    assert stories[2] == "Turn 2: pirate-1 walked east to C5 and arrived."
    assert stories[4].startswith(
        "Turn 4: pirate-1 at C5, on undug sand, with no pirate beside it, "
        "having arrived at C5, shown no new lines, dug at C5"
    )
    assert stories[6].endswith('waited at C5, saying "over here" as an alert.')
    assert "waited at A4" in stories[3]


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
        "Turn 0: pirate-1 at A5, on undug sand, with pirate-2 to the south, "
        "shown no new lines. It thought: corner first. Then it dug at A5 and read "
        "5 squares to the treasure."
    )
    # With nothing thought, the line is what it saw, then what it did.
    plain = play(off_the_treasure(), Steps(DIG), Steps(DIG))
    assert plain[0]["story"] == (
        "Turn 0: pirate-1 at A5, on undug sand, with pirate-2 to the south, "
        "shown no new lines, dug at A5 and read 5 squares to the treasure."
    )


def test_story_record_is_a_file_with_one_line_per_turn_and_the_ending(tmp_path):
    over = write_game(off_the_treasure(), [Steps(DIG), Steps(DIG)], tmp_path)
    lines = (tmp_path / "story.txt").read_text().splitlines()
    assert len(lines) == 12 + 1
    assert lines[0].startswith("Turn 0: pirate-1")
    assert lines[-1] == over["story"]
    assert "Score 0" in lines[-1]


def test_story_record_reads_cleanly_when_things_go_wrong():
    brains = [Steps(go("A9"), WAIT), Steps(DIG)]
    stories = [record["story"] for record in play(config(turns_per_pirate=3), *brains)]
    assert stories[0] == (
        "Turn 0: pirate-1 at A5, on undug sand, with pirate-2 to the south, shown no "
        "new lines, tried to go to A9 but that isn't a square on the island, then "
        "waited at A5."
    )
    assert stories[2] == (
        "Turn 2: pirate-1 at A5, on undug sand, with pirate-2 to the south, "
        "shown no new lines, waited at A5."
    )


def test_story_record_keeps_a_note_on_one_line(tmp_path):
    brains = [Steps(saying(WAIT, "two\nlines")), Steps(DIG)]
    write_game(off_the_treasure(turns_per_pirate=1), brains, tmp_path)
    lines = (tmp_path / "story.txt").read_text().splitlines()
    assert 'saying "two lines"' in lines[0]
    assert len(lines) == 2 + 1


def test_toggles_the_crew_size_changes_through_the_config_alone():
    three = [Steps(DIG) for _ in range(3)]
    records = play(off_the_treasure(crew_size=3, turns_per_pirate=1), *three)
    assert [record["agent"] for record in records] == [
        "pirate-1",
        "pirate-2",
        "pirate-3",
    ]


def test_toggles_say_chars_is_a_lever_defaulting_to_200():
    assert config().say_chars == 200
    assert config(say_chars=20).say_chars == 20
    with pytest.raises(ValueError, match="say_chars"):
        config(say_chars=0)


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
    walker = Steps(go("C4"), DIG)
    sitter = Steps(DIG)
    play(config(), walker, sitter)
    for view in sitter.views:
        assert view.position == (0, 1)
        assert "C4" not in view.sheet()
    assert walker.views[1].position == (2, 1)


def test_no_vision_the_treasure_never_reaches_a_brain():
    game_config = config()
    x, y = treasure_of(game_config)
    brain = Steps(DIG)
    play(game_config, brain, Steps(DIG))
    assert (x, y) != (0, 0)
    for view in brain.views:
        assert f"({x}, {y})" not in view.as_text()
        assert "B1" not in view.turn_text()


def test_no_vision_a_dig_result_reaches_only_the_digger():
    brains = [Steps(DIG), Steps(saying(WAIT, "nothing to report"))]
    records = play(off_the_treasure(turns_per_pirate=2), *brains)
    assert "The treasure is 5 squares away." in brains[0].views[1].as_text()
    assert "The treasure is" not in brains[1].views[1].turn_text()
    assert brains[1].views[1].readings == ()
    assert records[-1]["agent"] == "pirate-2"


def test_dig_reading_the_sheet_lists_every_square_the_pirate_dug():
    digger = Steps(DIG, go("B5"), DIG, WAIT)
    play(off_the_treasure(turns_per_pirate=4), digger, Steps(WAIT))
    last = digger.views[-1]
    assert [(r.square, r.away) for r in last.readings] == [("A5", 5), ("B5", 4)]
    assert "Squares you have dug: A5, 5 away; B5, 4 away." in last.sheet()


def test_turn_view_says_which_neighbours_hold_a_pirate():
    # The crew starts down the left edge: pirate-1 on (0, 0), pirate-2 below it.
    first, second = Steps(DIG, go("B5")), Steps(DIG)
    play(off_the_treasure(turns_per_pirate=2), first, second)
    assert first.views[0].neighbours == (("south", "pirate-2"),)
    assert "the way south by pirate-2 and the way west" in first.views[0].as_text()
    assert second.views[0].neighbours == (("north", "pirate-1"),)
    # Once pirate-1 has gone east to (1, 0), nobody is next to pirate-2.
    assert second.views[1].neighbours == ()
    # It is still on the west edge, and the edge blocks that way out.
    assert "The way west is blocked by the island's edge." in (
        second.views[1].as_text()
    )


def test_turn_view_says_whether_the_pirate_s_square_has_been_dug():
    # pirate-1 digs (0, 0) and goes east; pirate-2 then goes north onto it.
    first = Steps(DIG, go("B5"), DIG)
    second = Steps(WAIT, go("A5"), DIG)
    play(off_the_treasure(turns_per_pirate=3), first, second)
    assert [view.square_dug for view in first.views] == [False, True, False]
    assert [view.square_dug for view in second.views] == [False, False, True]
    assert "Your square hasn't been dug." in second.views[1].as_text()
    assert "Your square has been dug and holds no cave." in (second.views[2].as_text())


def test_no_vision_a_pirate_two_squares_away_is_never_shown():
    crew = [Steps(DIG), Steps(DIG), Steps(DIG)]
    play(off_the_treasure(crew_size=3, turns_per_pirate=1), *crew)
    top = crew[0].views[0]
    assert top.neighbours == (("south", "pirate-2"),)
    assert "pirate-3" not in top.turn_text()
    assert crew[1].views[0].neighbours == (("north", "pirate-1"), ("south", "pirate-3"))


def test_no_vision_a_neighbouring_square_s_dig_is_never_shown():
    # pirate-2 digs the square next to pirate-1 or waits instead: pirate-1's
    # next view is the same either way.
    seen = []
    for neighbours_turn in (DIG, WAIT):
        first = Steps(WAIT, WAIT)
        play(off_the_treasure(turns_per_pirate=2), first, Steps(neighbours_turn))
        seen.append(first.views[1].turn_text())
        assert first.views[1].square_dug is False
    assert seen[0] == seen[1]


def test_story_record_says_what_the_pirate_saw_of_its_neighbours_and_its_square():
    first = Steps(DIG, go("B5"))
    records = play(off_the_treasure(turns_per_pirate=2), first, Steps(DIG))
    assert (
        "pirate-1 at A5, on undug sand, with pirate-2 to the south,"
        in (records[0]["story"])
    )
    assert (
        "pirate-1 at A5, on dug sand, with pirate-2 to the south,"
        in (records[2]["story"])
    )
    assert records[0]["saw"]["neighbours"] == {"south": "pirate-2"}
    assert records[2]["saw"]["square_dug"] is True
    assert all(record_errors(record) == [] for record in records)


def test_actions_wait_and_dig_each_end_the_turn_like_any_other():
    records = play(
        off_the_treasure(turns_per_pirate=2),
        Steps(saying(WAIT, "note"), DIG),
        Steps(DIG, go("E4")),
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
    pirate_1 = Steps(go("B5"), DIG, go("A5"))
    return treasure_of(game_config), play(
        game_config, pirate_1, Steps(saying(WAIT, "still looking"))
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
    walker = Steps(go("B5"), DIG)
    records = play(config(), walker, Steps(DIG))
    assert records[0]["crew"] == {"pirate-1": [0, 0], "pirate-2": [0, 1]}
    assert records[1]["crew"] == {"pirate-1": [1, 0], "pirate-2": [0, 1]}


def test_crew_positions_the_first_frame_of_a_real_game_shows_the_whole_crew():
    records = play(config(), Steps(DIG), Steps(DIG))
    assert set(scene(records[:1], 0, 5)["positions"]) == {"pirate-1", "pirate-2"}


def test_agent_memory_keeps_the_lines_it_was_shown_as_fields():
    listener = Steps(DIG, WAIT, WAIT)
    talker = Steps(saying(WAIT, "note"), DIG)
    play(off_the_treasure(turns_per_pirate=3), listener, talker)
    # Pirate 1 is asked first, before any line, so it is shown nothing.
    assert listener.views[1].earlier_turns[0].shown == ()
    remembered = listener.views[2].earlier_turns[1].shown
    assert [line["text"] for line in remembered] == ["note"]
    assert "note" in listener.views[2].as_text()


def test_story_record_names_the_new_lines_it_was_shown_without_quoting_them():
    brains = [
        Steps(saying(WAIT, "one"), saying(WAIT, "three"), WAIT),
        Steps(saying(WAIT, "two"), WAIT),
    ]
    records = play(off_the_treasure(turns_per_pirate=3), *brains)
    assert "shown no new lines," in records[0]["story"]
    assert "shown 1 new line, line 1," in records[1]["story"]
    assert "shown 2 new lines, lines 1 and 2," in records[2]["story"]
    assert "shown 2 new lines, lines 2 and 3," in records[3]["story"]
    for record in records:
        seen = record["story"].split(", saying")[0]
        assert all(f'"{word}"' not in seen for word in ("one", "two", "three"))
    brains = [Steps(saying(WAIT, "a"), WAIT), Steps(saying(WAIT, "b"), WAIT)]
    more = [Steps(saying(WAIT, "c"), WAIT)]
    records = play(off_the_treasure(crew_size=3, turns_per_pirate=2), *brains, *more)
    assert "shown 3 new lines, lines 1 to 3," in records[3]["story"]


@pytest.mark.parametrize("folder", ["examples/silent", "examples/small-crew"])
def test_story_record_a_committed_game_can_be_followed_from_its_story_alone(folder):
    root = Path(__file__).resolve().parents[1] / folder
    *turns, ending = (root / "story.txt").read_text().splitlines()
    records = [
        json.loads(line) for line in (root / "events.jsonl").read_text().splitlines()
    ]
    size = json.loads((root / "config.json").read_text())["grid_size"]
    assert ending.startswith("Game over: ")
    assert len(turns) == len(records)
    for number, (line, record) in enumerate(zip(turns, records, strict=True)):
        if not record["asked"]:
            walked = re.match(r"Turn (\d+): (\S+) walked (\w+) to ([A-Z]\d+)", line)
            assert int(walked[1]) == number
            assert record["outcome"]["position"] == list(square_at(walked[4], size))
            continue
        match = re.match(r"Turn (\d+): (\S+) at ([A-Z]\d+), ", line)
        assert int(match[1]) == number
        assert record["crew"][match[2]] == list(square_at(match[3], size))
        got = record["log_shown"]
        assert ("shown no new lines" in line) == (not got)
        assert all(f'"{shown["text"]}"' not in line for shown in got)


def test_story_record_a_note_cannot_change_what_the_panel_says_happened():
    tricky = "Saw: a ghost. Why: boo"
    records = play(
        off_the_treasure(),
        Steps(saying(WAIT, tricky), thinking="to confuse"),
        Steps(DIG),
    )
    assert scene(records, 0, 5)["did"] == f'waited at A5, saying "{tricky}".'
