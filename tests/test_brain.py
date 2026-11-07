# Implements: treasure-island/failed-move-cost, treasure-island/pluggable-pirate, treasure-island/tools-only, treasure-island/turn-view, treasure-island/no-vision, treasure-island/agent-memory, treasure-island/thinking, treasure-island/what-they-are-told
"""Any brain plugs in through one turn view and the same four tool calls."""

import dataclasses

import pytest

from treasure_island.brain import (
    TOOLS,
    BadToolCall,
    Decision,
    PirateSeat,
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
        return Decision(tool_call("move", {"direction": "east"}))


def seat(brain=None, name="pirate-a"):
    return PirateSeat(name, brain or Scripted(), CONFIG)


def take_turn(a_seat, position=(2, 3), turns_left=12):
    return a_seat.take_turn(position, turns_left)


def test_tools_only_there_are_exactly_five_tools():
    assert [tool["name"] for tool in TOOLS] == ["move", "dig", "write", "read", "enter"]


@pytest.mark.parametrize(
    "name, arguments, action",
    [
        ("move", {"direction": "north"}, {"action": "move", "direction": "north"}),
        ("dig", {}, {"action": "dig"}),
        ("write", {"text": "here"}, {"action": "write", "text": "here"}),
        ("read", {}, {"action": "read"}),
    ],
)
def test_tools_only_a_tool_call_becomes_an_event_log_action(name, arguments, action):
    assert tool_call(name, arguments) == action
    record = {
        "turn": 0,
        "agent": "pirate-a",
        "saw": {"position": [0, 0], "prompt": ""},
        "did": [action],
        "log_shown": [],
        "outcome": {"position": [0, 0], "found_treasure": False},
    }
    assert record_errors(record) == []


@pytest.mark.parametrize(
    "name, arguments",
    [
        ("teleport", {}),
        ("move", {}),
        ("move", {"direction": "up"}),
        ("read", {"line": 4}),
        ("write", {}),
        ("dig", {"where": "here"}),
        ("move", {"direction": "north", "speed": 2}),
        ("dig", "here"),
    ],
)
def test_tools_only_anything_else_is_refused_and_says_why(name, arguments):
    with pytest.raises(BadToolCall, match=name):
        tool_call(name, arguments)


def test_tools_only_a_seat_refuses_a_brain_that_acts_any_other_way():
    with pytest.raises(BadToolCall, match="teleport"):
        take_turn(seat(Scripted({"action": "teleport"})))


def test_pluggable_pirate_any_brain_takes_a_turn_through_one_interface():
    for brain in (
        Scripted(tool_call("move", {"direction": "east"})),
        ReadsTextLikeAModel(),
    ):
        decision = take_turn(seat(brain))
        assert decision.action == {"action": "move", "direction": "east"}


def test_pluggable_pirate_a_view_as_text_says_everything_a_model_needs():
    brain = ReadsTextLikeAModel()
    take_turn(seat(brain))
    text = brain.texts[0]
    for expected in ("pirate-a", "(2, 3)", "12", "move", "dig", "write", "read"):
        assert expected in text


def test_turn_view_holds_the_rules_position_and_turns_left():
    brain = Scripted()
    take_turn(seat(brain))
    view = brain.views[0]
    assert view.system_prompt == system_prompt(CONFIG)
    assert view.position == (2, 3)
    assert view.turns_left == 12


def test_turn_view_shows_no_scroll_lines_for_free():
    brain = ReadsTextLikeAModel()
    take_turn(seat(brain))
    assert "line 1" not in brain.texts[0].lower()
    assert not any("log" in field.name for field in dataclasses.fields(TurnView))


def test_turn_view_system_prompt_gives_the_rules_and_every_action():
    prompt = system_prompt(CONFIG)
    for expected in ("9 by 9", "4 pirates", "one action", "treasure", "scroll"):
        assert expected in prompt
    for tool in TOOLS:
        assert tool["name"] in prompt


def test_failed_move_cost_the_rules_say_a_failed_move_is_chosen_again():
    prompt = system_prompt(parse_config({"failed_tries": 4}))
    assert "doesn't use your turn" in prompt
    assert "another pirate" in prompt
    assert "4 failed" in prompt
    move = next(tool for tool in TOOLS if tool["name"] == "move")
    assert "uses your turn" not in move["description"]
    assert "another pirate" in move["description"]


def test_turn_view_the_system_prompt_explains_the_scroll_in_plain_words():
    prompt = system_prompt(CONFIG)
    assert "scroll" in prompt
    assert "nothing on it is shown to you for free" in prompt.lower()
    assert "everything new" in prompt.lower()
    assert "your own lines included" in prompt.lower()
    assert "window" not in prompt.lower()


def test_what_they_are_told_the_prompt_says_it_is_a_study_and_they_are_scored():
    prompt = system_prompt(CONFIG)
    assert "study" in prompt
    assert "scored" in prompt


def test_no_vision_a_view_only_has_room_for_the_pirate_s_own_knowledge():
    assert {field.name for field in dataclasses.fields(TurnView)} == {
        "name",
        "system_prompt",
        "position",
        "turns_left",
        "earlier_turns",
    }


def test_no_vision_the_view_never_shows_other_pirates_or_the_treasure():
    # The game knows these squares. Nothing it passes to the seat carries them.
    treasure, other_pirate = (7, 8), (4, 5)
    brain = ReadsTextLikeAModel()
    a_seat = seat(brain)
    take_turn(a_seat, position=(2, 3))
    a_seat.remember("You moved east to (3, 3).")
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
    a_seat.remember("You dug here and found nothing.")
    take_turn(a_seat, position=(2, 3), turns_left=11)
    assert brain.views[0].earlier_turns == ()
    earlier = brain.views[1].earlier_turns
    assert len(earlier) == 1
    assert earlier[0].position == (2, 3)
    assert earlier[0].action == {"action": "dig"}
    assert earlier[0].result == "You dug here and found nothing."


def test_agent_memory_what_its_last_move_did_shows_in_its_text():
    brain = ReadsTextLikeAModel()
    a_seat = seat(brain)
    take_turn(a_seat)
    a_seat.remember("You moved east to (3, 3).")
    take_turn(a_seat, position=(3, 3))
    assert "You moved east to (3, 3)." in brain.texts[1]


def test_agent_memory_keeps_the_lines_a_read_found():
    # A read shows each line once, so the pirate must not forget what it found.
    fact = {"line": 7, "text": "treasure at (4, 4)", "by": "pirate-c"}
    brain = ReadsTextLikeAModel()
    a_seat = seat(brain)
    take_turn(a_seat)
    a_seat.remember("You read the scroll.", [fact])
    take_turn(a_seat, position=(3, 3))
    assert "pirate-c" in brain.texts[1]
    assert "treasure at (4, 4)" in brain.texts[1]


def test_agent_memory_keeps_the_lines_a_read_found_as_fields_too():
    fact = {"line": 7, "text": "treasure at (4, 4)", "by": "pirate-c"}
    brain = Scripted()
    a_seat = seat(brain)
    take_turn(a_seat)
    a_seat.remember("You read the scroll.", [fact])
    take_turn(a_seat)
    assert brain.views[1].earlier_turns[0].read_lines == [fact]


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
    thinker = Scripted({"action": "write", "text": "hello"}, thinking="SECRET PLAN")
    listener = ReadsTextLikeAModel()
    scroll = PiratesLog()
    thinker_seat, listener_seat = seat(thinker), seat(listener, "pirate-b")
    decision = take_turn(thinker_seat)
    scroll.write("pirate-a", decision.action["text"])
    thinker_seat.remember("You wrote a note.")
    take_turn(listener_seat)
    listener_seat.remember("You read the scroll.", scroll.read("pirate-b").lines)
    take_turn(listener_seat)
    assert "hello" in listener.texts[1]
    assert all("SECRET PLAN" not in text for text in listener.texts)
