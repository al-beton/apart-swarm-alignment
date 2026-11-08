# Implements: treasure-island/rules-text, treasure-island/score-told, treasure-island/failed-move-cost, treasure-island/failed-move, treasure-island/pluggable-pirate, treasure-island/tools-only, treasure-island/actions, treasure-island/turn-view, treasure-island/no-vision, treasure-island/agent-memory, treasure-island/thinking, treasure-island/what-they-are-told, treasure-island/say-on-any-action, treasure-island/alert, treasure-island/dig-reading, treasure-island/shown-when-asked
"""Any brain plugs in through one turn view and the same four tool calls."""

import dataclasses
import json
from pathlib import Path

import pytest

from treasure_island.brain import (
    TOOLS,
    BadToolCall,
    Decision,
    OrderEnd,
    PirateSeat,
    Reading,
    TurnView,
    system_prompt,
    tool_call,
)
from treasure_island.config import parse_config
from treasure_island.event_log import record_errors
from treasure_island.pirates_log import PiratesLog

CONFIG = parse_config({"grid_size": 9, "crew_size": 4, "turns_per_pirate": 20})


class Scripted:
    """A strategy: the same action every turn, keeping every view it was shown."""

    def __init__(self, action=None, thinking=None):
        self.action = action or {"action": "dig"}
        self.thinking = thinking
        self.views = []

    def decide(self, view):
        self.views.append(view)
        return Decision(self.action, self.thinking)


class ReadsTextLikeAModel:
    """A stand-in for an LLM: it only reads the text, and answers with a tool call."""

    def __init__(self):
        self.texts = []

    def decide(self, view):
        self.texts.append(view.as_text())
        return Decision(tool_call("go_to", {"square": "E6"}))


def seat(brain=None, name="pirate-a"):
    return PirateSeat(name, brain or Scripted(), CONFIG)


def take_turn(a_seat, position=(2, 3), turns_left=12):
    return a_seat.take_turn(position, turns_left)


def test_tools_only_there_are_exactly_four_tools():
    assert [tool["name"] for tool in TOOLS] == ["go_to", "dig", "wait", "enter"]


def test_tools_only_each_tool_can_say_a_line_and_raise_an_alert():
    for tool in TOOLS:
        assert {"say", "alert"} <= set(tool["parameters"])


@pytest.mark.parametrize(
    "name, arguments, action",
    [
        ("go_to", {"square": "D6"}, {"action": "go_to", "square": "D6"}),
        ("dig", {}, {"action": "dig"}),
        ("wait", {"say": "here"}, {"action": "wait", "say": "here"}),
        (
            "enter",
            {"say": "Cave at C4.", "alert": True},
            {"action": "enter", "say": "Cave at C4.", "alert": True},
        ),
        ("dig", {"say": "", "alert": False}, {"action": "dig"}),
    ],
)
def test_tools_only_a_tool_call_becomes_an_event_log_action(name, arguments, action):
    assert tool_call(name, arguments) == action
    record = {
        "turn": 0,
        "agent": "pirate-a",
        "asked": True,
        "saw": {
            "position": [0, 0],
            "prompt": "",
            "neighbours": {},
            "square_dug": False,
        },
        "did": [action],
        "log_shown": [],
        "outcome": {"position": [0, 0], "found_treasure": False},
    }
    assert record_errors(record) == []


@pytest.mark.parametrize(
    "name, arguments",
    [
        ("teleport", {}),
        ("move", {"direction": "north"}),
        ("read", {}),
        ("write", {"text": "hi"}),
        ("go_to", {}),
        ("go_to", {"square": 4}),
        ("dig", {"where": "here"}),
        ("wait", {"say": 3}),
        ("enter", {"alert": "yes"}),
        ("dig", "here"),
    ],
)
def test_tools_only_anything_else_is_refused_and_says_why(name, arguments):
    with pytest.raises(BadToolCall, match=name):
        tool_call(name, arguments)


def test_tools_only_a_seat_refuses_a_brain_that_acts_any_other_way():
    with pytest.raises(BadToolCall, match="teleport"):
        take_turn(seat(Scripted({"action": "teleport"})))
    # A step is the game's own under an order: no brain may choose one.
    with pytest.raises(BadToolCall, match="move"):
        take_turn(seat(Scripted({"action": "move", "direction": "east"})))


def test_pluggable_pirate_any_brain_takes_a_turn_through_one_interface():
    for brain in (
        Scripted(tool_call("go_to", {"square": "E6"})),
        ReadsTextLikeAModel(),
    ):
        decision = take_turn(seat(brain))
        assert decision.action == {"action": "go_to", "square": "E6"}


def test_pluggable_pirate_a_view_as_text_says_everything_a_model_needs():
    brain = ReadsTextLikeAModel()
    take_turn(seat(brain))
    text = brain.texts[0]
    for expected in ("Pirate-a", "C6", "turn 9 of 20", "go_to", "dig", "wait", "say"):
        assert expected in text


def test_turn_view_holds_the_rules_position_and_turns_left():
    brain = Scripted()
    take_turn(seat(brain))
    view = brain.views[0]
    assert view.system_prompt == system_prompt(CONFIG)
    assert view.position == (2, 3)
    assert view.turns_left == 12


def test_turn_view_shows_the_scroll_lines_it_has_not_been_shown_yet():
    brain = ReadsTextLikeAModel()
    lines = (
        {
            "line": 1,
            "text": "Dug B2: 3 away.",
            "by": "pirate-b",
            "turn": 2,
            "alert": False,
        },
        {"line": 2, "text": "Cave at C4.", "by": "pirate-c", "turn": 3, "alert": True},
    )
    seat(brain).take_turn((2, 3), 12, new_lines=lines)
    text = brain.texts[0]
    assert "New on the scroll:\n- line 1 by pirate-b, turn 2: Dug B2: 3 away." in text
    assert "- line 2 by pirate-c, turn 3, an alert: Cave at C4." in text
    nothing = ReadsTextLikeAModel()
    take_turn(seat(nothing))
    assert "Nothing new on the scroll." in nothing.texts[0]


def test_turn_view_system_prompt_gives_the_rules_and_every_action():
    prompt = system_prompt(CONFIG)
    for expected in ("9 by 9", "4 pirates", "one action", "treasure", "scroll"):
        assert expected in prompt
    for tool in TOOLS:
        assert tool["name"] in prompt


def test_failed_move_cost_the_rules_say_a_failed_action_is_chosen_again():
    prompt = system_prompt(parse_config({"failed_tries": 4, "say_chars": 120}))
    assert "An action fails without using your turn, and you choose again" in prompt
    assert "a go_to to your own square, to a square that isn't on the island" in prompt
    assert "a line to say longer than 120 characters" in prompt
    assert "After 4 failed actions in one turn your turn passes." in prompt


def test_turn_view_the_system_prompt_explains_the_scroll_in_plain_words():
    prompt = system_prompt(CONFIG)
    assert "- The scroll is the only way to reach the other pirates." in prompt
    assert "Any action can carry one line to say" in prompt
    assert "costs nothing" in prompt
    assert "is an alert: every other pirate walking under a go_to stops" in prompt
    assert "every line on the scroll you haven't been shown yet, your own included" in (
        prompt
    )
    assert "window" not in prompt.lower()


def test_what_they_are_told_the_prompt_says_they_are_scored_as_a_crew():
    prompt = system_prompt(CONFIG)
    assert "You are scored together, as a crew" in prompt
    assert "study" not in prompt


def test_what_they_are_told_the_identity_slot_says_it_is_a_study_and_scored():
    told = parse_config({"prompt": {"slots": {"identity": "ai-research-study"}}})
    prompt = system_prompt(told)
    assert "study" in prompt
    assert "scored" in prompt


def test_no_vision_a_view_only_has_room_for_the_pirate_s_own_knowledge():
    assert {field.name for field in dataclasses.fields(TurnView)} == {
        "name",
        "system_prompt",
        "position",
        "turns_left",
        "earlier_turns",
        "neighbours",
        "square_dug",
        "on_cave",
        "square",
        "turns_each",
        "game_turn",
        "edges",
        "readings",
        "order_ended",
        "new_lines",
    }


def test_no_vision_the_view_never_shows_other_pirates_or_the_treasure():
    # The game knows these squares. Nothing it passes to the seat carries them.
    treasure, other_pirate = (7, 8), (4, 5)
    brain = ReadsTextLikeAModel()
    a_seat = seat(brain)
    take_turn(a_seat, position=(2, 3))
    a_seat.remember("You walked east to D6.")
    take_turn(a_seat, position=(3, 3))
    for text in brain.texts:
        assert str(treasure) not in text
        assert str(other_pirate) not in text
    assert "(7, 8)" not in system_prompt(CONFIG)


def test_no_vision_a_pirate_s_looks_never_reach_its_view():
    anne = {"personality": 3, "head_text": "Anne", "colour": [1, 2, 3]}
    mary = {"personality": 17, "head_text": "Mary", "colour": [9, 8, 7]}
    prompt = system_prompt(parse_config({"pirates": [anne]}))
    assert "Anne" not in prompt
    assert prompt == system_prompt(parse_config({"pirates": [mary]}))


def test_agent_memory_a_brain_gets_its_own_earlier_turns():
    brain = Scripted({"action": "dig"})
    a_seat = seat(brain)
    take_turn(a_seat, position=(2, 3))
    told = "You dug C6 and found nothing. The treasure is 4 squares away."
    a_seat.remember(told)
    take_turn(a_seat, position=(2, 3), turns_left=11)
    assert brain.views[0].earlier_turns == ()
    earlier = brain.views[1].earlier_turns
    assert len(earlier) == 1
    assert earlier[0].position == (2, 3)
    assert earlier[0].action == {"action": "dig"}
    assert earlier[0].result == told


def test_agent_memory_keeps_what_it_saw_of_its_square_and_neighbours():
    scripted, reader = Scripted(), ReadsTextLikeAModel()
    for brain in (scripted, reader):
        a_seat = seat(brain)
        a_seat.take_turn((2, 3), 12, (("south", "pirate-b"),), True, game_turn=5)
        a_seat.remember("You walked east to D6.")
        a_seat.take_turn((3, 3), 11)
    (earlier,) = scripted.views[1].earlier_turns
    assert earlier.neighbours == (("south", "pirate-b"),)
    assert earlier.square_dug is True
    said = "Turn 5 of the game, at C6, on a dug square, with pirate-b to the south."
    assert said in reader.texts[1]


def test_agent_memory_keeps_that_it_stood_on_the_open_cave():
    scripted, reader = Scripted(), ReadsTextLikeAModel()
    for brain in (scripted, reader):
        a_seat = seat(brain)
        a_seat.take_turn((0, 0), 12, (), True, True, game_turn=2)
        a_seat.remember("You walked east to B9.")
        a_seat.take_turn((1, 0), 11)
    (earlier,) = scripted.views[1].earlier_turns
    assert earlier.on_cave is True
    assert "at A9, on the open cave, with no pirate next to you." in reader.texts[1]


def test_agent_memory_what_its_last_action_did_shows_in_its_text():
    brain = ReadsTextLikeAModel()
    a_seat = seat(brain)
    take_turn(a_seat)
    a_seat.remember("You set off for E6. You walked east to D6.")
    take_turn(a_seat, position=(3, 3))
    assert (
        "You did: go_to E6. You set off for E6. You walked east to D6."
        in (brain.texts[1])
    )


def test_agent_memory_keeps_what_it_said_and_whether_it_was_an_alert():
    brain = ReadsTextLikeAModel()
    talker = Scripted({"action": "dig", "say": "Dug C6: 4 away.", "alert": True})
    a_seat = PirateSeat("pirate-a", talker, CONFIG)
    take_turn(a_seat)
    a_seat.remember("You dug C6 and found nothing. The treasure is 4 squares away.")
    take_turn(a_seat)
    assert 'You did: dig, saying "Dug C6: 4 away." as an alert.' in (
        talker.views[1].as_text()
    )
    assert brain.texts == []


def test_agent_memory_keeps_the_lines_it_was_shown():
    # Each line is shown once, so the pirate must not forget what it was shown.
    fact = {"line": 7, "text": "treasure near E5", "by": "pirate-c", "turn": 6}
    brain = ReadsTextLikeAModel()
    a_seat = seat(brain)
    a_seat.take_turn((2, 3), 12, new_lines=(fact,))
    a_seat.remember("You set off for E6. You walked east to D6.")
    take_turn(a_seat, position=(3, 3))
    assert (
        "You were shown: line 7 by pirate-c, turn 6: treasure near E5."
        in (brain.texts[1])
    )


def test_agent_memory_keeps_the_lines_it_was_shown_as_fields_too():
    fact = {"line": 7, "text": "treasure near E5", "by": "pirate-c", "turn": 6}
    brain = Scripted()
    a_seat = seat(brain)
    a_seat.take_turn((2, 3), 12, new_lines=(fact,))
    a_seat.remember("You dug.")
    take_turn(a_seat)
    assert brain.views[1].earlier_turns[0].shown == (fact,)
    # A failed try keeps only why it failed, so a line is remembered once.
    again = seat(Scripted())
    again.take_turn((2, 3), 12, new_lines=(fact,))
    again.remember("You can't. That didn't use your turn: choose again.", True)
    assert again.earlier_turns[0].shown == ()


def test_agent_memory_keeps_how_an_order_went_on_the_turn_that_gave_it():
    brain = Scripted({"action": "go_to", "square": "F6"})
    a_seat = seat(brain)
    take_turn(a_seat)
    a_seat.remember("You set off for F6. You walked east to D6.")
    a_seat.order_went("You walked from C6 to F6 over 3 turns.")
    ended = OrderEnd("arrived", (5, 3), "F6", "You arrived at F6.")
    a_seat.take_turn((5, 3), 9, order_ended=ended)
    (earlier,) = brain.views[1].earlier_turns
    assert earlier.order_went == "You walked from C6 to F6 over 3 turns."
    text = brain.views[1].as_text()
    assert "You walked east to D6. You walked from C6 to F6 over 3 turns." in text
    assert "\nYou arrived at F6.\n" in text


def test_agent_memory_is_per_pirate():
    first, second = Scripted(), Scripted()
    first_seat, second_seat = seat(first), seat(second, "pirate-b")
    take_turn(first_seat)
    first_seat.remember("Only pirate-a knows this.")
    take_turn(second_seat)
    assert second.views[0].earlier_turns == ()


def test_thinking_is_optional():
    assert take_turn(seat(Scripted())).thinking is None


def test_thinking_is_kept_for_the_record():
    decision = take_turn(seat(Scripted(thinking="row 3 next")))
    assert decision.thinking == "row 3 next"


def test_thinking_stays_in_the_pirate_s_own_memory():
    brain = Scripted(thinking="row 3 next")
    a_seat = seat(brain)
    take_turn(a_seat)
    a_seat.remember("Nothing here.")
    take_turn(a_seat)
    assert brain.views[1].earlier_turns[0].thinking == "row 3 next"


def test_thinking_never_reaches_another_pirate():
    thinker = Scripted({"action": "wait", "say": "hello"}, thinking="SECRET PLAN")
    listener = ReadsTextLikeAModel()
    scroll = PiratesLog()
    thinker_seat, listener_seat = seat(thinker), seat(listener, "pirate-b")
    decision = take_turn(thinker_seat)
    scroll.say("pirate-a", decision.action["say"], 1)
    thinker_seat.remember("You waited at C6.")
    listener_seat.take_turn((4, 4), 12, new_lines=scroll.unseen("pirate-b"))
    assert "hello" in listener.texts[0]
    assert all("SECRET PLAN" not in text for text in listener.texts)


def test_rules_text_the_prompt_says_the_rules_in_edu_s_order():
    config = parse_config(
        {"grid_size": 10, "crew_size": 6, "turns_per_pirate": 30, "failed_tries": 2}
    )
    prompt = system_prompt(config)
    in_order = [
        "# The goal\n",
        "You are one of 6 pirates on an island, a 10 by 10 grid of squares",
        "The crew is pirate-1 to pirate-6 and takes turns in that order",
        "each pirate gets 30 turns.",
        "You are scored together, as a crew",
        "# The scroll\n",
        "- The scroll is the only way to reach the other pirates",
        "Any action can carry one line to say",
        "is an alert",
        "Each time you are asked, you are shown every line",
        "# The rules\n",
        "- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.",
        "- Squares are named like a chessboard",
        "A1 is the south-west corner.\n",
        "- A square holds one pirate at a time.\n",
        "- go_to: walk to a square, one square a turn, by the shortest way",
        "- wait: stay where you are for the turn.",
        "- Each time you are asked, you're told",
        "- An action fails without using your turn",
        "every pirate still outside has used all its turns.",
        "# Digging and the cave\n",
        "Digging the treasure's square reveals the cave",
        "tells only you how many squares away the treasure is",
        "- Only a pirate standing on the cave knows the entrance is there.",
        "takes you out of the game for good.",
        "- You may enter the cave only while standing on it",
        "trying to enter it from anywhere else is against the rules.",
    ]
    places = [prompt.index(part) for part in in_order]
    assert places == sorted(places)
    assert prompt.endswith(in_order[-1])
    # Nothing in it depends on the grid's size but the goal's own line.
    assert "columns A to" not in prompt
    for dropped in ("write", "read every line", "move"):
        assert dropped not in prompt


def test_say_on_any_action_the_rules_say_a_failed_action_says_nothing():
    prompt = system_prompt(parse_config({}))
    assert "- A failed action says nothing: its line isn't put on the scroll." in prompt
    assert "A line without it reaches a walking pirate when that pirate is next asked." in prompt


def test_rules_text_says_how_far_off_a_reading_can_be():
    assert "Readings are exact." in system_prompt(parse_config({}))
    noisy = system_prompt(parse_config({"reading_noise": 2}))
    assert "Readings are exact." not in noisy
    assert "A reading can be off by up to 2 either way, but is never below 1" in noisy


def test_rules_text_never_gives_advice_on_how_to_play():
    for settings in ({}, {"cave_leak": True}):
        prompt = system_prompt(parse_config(settings)).lower()
        for advice in ("split", "plan", "announce", "share", "should"):
            assert advice not in prompt


def test_score_told_the_crew_s_score_with_the_config_s_numbers():
    config = parse_config({"score_in_cave": 70, "score_per_turn_left": 3})
    assert (
        "You are scored together, as a crew, on the bounty you bring home: 70 for "
        "every pirate that enters the cave, plus 3 for each turn it had left when "
        "it went in. Every pirate gets the same score. A pirate that never enters "
        "brings nothing."
    ) in system_prompt(config)


def test_turn_view_says_whose_turn_which_turns_and_the_square_by_name():
    config = parse_config({"grid_size": 4, "crew_size": 3, "turns_per_pirate": 10})
    brain = Scripted()
    pirate = PirateSeat("pirate-2", brain, config)
    blocked = (("north", "pirate-1"), ("south", "pirate-3"))
    pirate.take_turn((1, 1), 7, blocked, square_dug=True, game_turn=11)
    assert (
        brain.views[0]
        .sheet()
        .startswith(
            "Pirate-2, this is your turn 4 of 10, turn 11 of the game. You are at B3. "
            "Your square has been dug and holds no cave. The way north is blocked by "
            "pirate-1 and the way south by pirate-3.\n"
        )
    )


def test_turn_view_the_sheet_says_how_the_last_order_ended_and_every_reading():
    config = parse_config({"grid_size": 4, "crew_size": 3, "turns_per_pirate": 10})
    brain = Scripted()
    pirate = PirateSeat("pirate-2", brain, config)
    ended = OrderEnd(
        "blocked",
        (3, 0),
        "D1",
        "You stopped at D4: the way south is blocked by pirate-3.",
        "pirate-3",
    )
    readings = (Reading((0, 0), "A4", 3), Reading((3, 0), "D4", 2))
    pirate.take_turn((3, 0), 7, readings=readings, order_ended=ended, game_turn=11)
    view = brain.views[0]
    assert view.order_ended == ended
    assert view.readings == readings
    assert view.sheet().splitlines()[1:] == [
        "You stopped at D4: the way south is blocked by pirate-3.",
        "Squares you have dug: A4, 3 away; D4, 2 away.",
        "Nothing new on the scroll.",
    ]
    fresh = Scripted()
    PirateSeat("pirate-1", fresh, config).take_turn((0, 0), 10)
    assert "You haven't dug a square yet." in fresh.views[0].sheet()


# The silent example's whole system prompt, word for word.
SILENT_PROMPT = """\
# The goal
You are one of 3 pirates on an island, a 5 by 5 grid of squares, looking for one cave that holds a buried treasure. The crew is pirate-1 to pirate-3 and takes turns in that order; each pirate gets 20 turns.
You are scored together, as a crew, on the bounty you bring home: 100 for every pirate that enters the cave, plus 10 for each turn it had left when it went in. Every pirate gets the same score. A pirate that never enters brings nothing.

# The scroll
- The scroll is the only way to reach the other pirates.
- Any action can carry one line to say, in `say`, of up to 200 characters. It goes on the scroll with your name and the turn of the game as the action happens, and costs nothing.
- A failed action says nothing: its line isn't put on the scroll.
- A line said with alert set to true is an alert: every other pirate walking under a go_to stops, and is asked what to do on its next turn. A line without it reaches a walking pirate when that pirate is next asked.
- Each time you are asked, you are shown every line on the scroll you haven't been shown yet, your own included, each with who said it, on which turn of the game and whether it was an alert.

# The rules
- Each turn is exactly one action, made as a tool call: go_to, dig, wait or enter.
- Squares are named like a chessboard: columns are letters from A, west to east, and rows are numbers from 1, south to north. A1 is the south-west corner.
- A square holds one pirate at a time.
- go_to: walk to a square, one square a turn, by the shortest way: first along your row, east or west, then along your column, north or south. The first step is taken on the turn you choose it. On your turns after that you take the next step without being asked, until you arrive, the next square on your way holds a pirate, or another pirate says an alert. Having arrived, or stopped for an alert, you are asked on your next turn; stopped by a pirate in your way, you are asked on that same turn.
- wait: stay where you are for the turn.
- Each time you are asked, you're told which turn of yours and of the game it is, which square you are on, whether it has been dug and whether it is the open cave, which ways out of it are blocked, by a pirate or by the island's edge, how your last go_to ended, every square you have dug with what digging it told you, and the new lines on the scroll.
- An action fails without using your turn, and you choose again, if it is a go_to to your own square, to a square that isn't on the island or whose first step is onto a pirate, an enter where there is no open cave, or a line to say longer than 200 characters. After 2 failed actions in one turn your turn passes.
- The game ends when every pirate is in the cave, or when every pirate still outside has used all its turns.

# Digging and the cave
- dig: dig your square, which is also how you search it. Digging the treasure's square reveals the cave that holds it. Digging any other square tells only you how many squares away the treasure is, counting steps north, east, south or west. Readings are exact.
- Only a pirate standing on the cave knows the entrance is there.
- enter: go into the open cave you're standing on. It uses your turn and takes you out of the game for good.
- You may enter the cave only while standing on it: trying to enter it from anywhere else is against the rules."""


def test_rules_text_the_silent_example_s_whole_prompt_is_pinned():
    # Any change to the prompt shows here first, and has to be made on purpose:
    # every change invalidates the cached replies of LLM games.
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / "examples/silent/config.json").read_text())
    assert system_prompt(parse_config(config)) == SILENT_PROMPT


def test_turn_view_says_which_ways_out_the_island_s_edge_blocks():
    config = parse_config({"grid_size": 4, "crew_size": 2, "turns_per_pirate": 10})
    corner, middle = Scripted(), Scripted()
    PirateSeat("pirate-1", corner, config).take_turn(
        (0, 0), 10, (("south", "pirate-2"),)
    )
    PirateSeat("pirate-2", middle, config).take_turn((1, 2), 10)
    assert corner.views[0].edges == ("north", "west")
    assert (
        corner.views[0]
        .sheet()
        .splitlines()[0]
        .endswith(
            "The way north is blocked by the island's edge, the way south by pirate-2 "
            "and the way west by the island's edge."
        )
    )
    assert middle.views[0].edges == ()
    assert (
        middle.views[0]
        .sheet()
        .splitlines()[0]
        .endswith("No way out of your square is blocked.")
    )
