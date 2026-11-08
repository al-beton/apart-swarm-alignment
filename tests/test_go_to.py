# Implements: treasure-island/go-to, treasure-island/status-sheet
"""Walking with go_to, with no model call per step, and the status sheet."""

import json

from treasure_island.brain import Decision, PirateSeat, system_prompt
from treasure_island.config import parse_config, save_config
from treasure_island.game_loop import Game
from treasure_island.llm import LLMPirate


class Script:
    """A scripted brain that plays its actions in order, then digs. It counts its calls."""

    def __init__(self, *actions):
        self.actions = list(actions)
        self.views = []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if self.actions else {"action": "dig"}
        return Decision(action)


def go_to(square):
    return {"action": "go_to", "square": square}


def played(brains, turns=10, **settings):
    config = parse_config(
        {
            "grid_size": 5,
            "crew_size": len(brains),
            "turns_per_pirate": turns,
            "seed": 3,
            "go_to": True,
            **settings,
        }
    )
    return list(Game(config, brains).records())


def test_go_to_walks_the_path_without_model_calls():
    brain = Script(go_to("E1"))
    records = played([brain])
    # The call's own turn takes the first step; seven more walk with no model call.
    assert records[0]["go_to"] == "E1"
    walked = [record["walked"] for record in records[1:8]]
    assert walked == ["E1"] * 7
    path = [record["outcome"]["position"] for record in records[:8]]
    assert path == [[1, 0], [2, 0], [3, 0], [4, 0], [4, 1], [4, 2], [4, 3], [4, 4]]
    assert all(record["did"][0]["action"] == "move" for record in records[:8])
    # Asked on the go_to turn, then not again until it has arrived.
    assert len(brain.views) == 1 + (len(records) - 8)
    assert "walked" not in records[8]
    assert "You arrived at E1." in records[7]["result"]


def test_go_to_stops_when_the_scroll_gains_a_line():
    walker = Script(go_to("E1"))
    writer = Script({"action": "dig"}, {"action": "write", "text": "Hello"})
    records = played([walker, writer])
    assert records[2]["walked"] == "E1"  # pirate-1 walks on while nobody writes
    assert records[3]["did"] == [{"action": "write", "text": "Hello"}]
    assert "walked" not in records[4]  # pirate-1 is asked again
    told = walker.views[1].turn_text()
    assert "Your walk to E1 stopped: someone wrote on the scroll." in told


def test_go_to_stops_when_a_pirate_blocks_the_way():
    walker = Script(go_to("B1"))
    other = Script({"action": "move", "direction": "east"})  # A4 to B4
    records = played([walker, other])
    assert records[0]["outcome"]["position"] == [1, 0]
    assert records[1]["outcome"]["position"] == [1, 1]
    assert "walked" not in records[2]
    told = walker.views[1].turn_text()
    assert "Your walk to B1 stopped: pirate-2 is in the way." in told


def test_go_to_takes_the_other_shortest_way_round_a_pirate():
    dig = {"action": "dig"}
    walker = Script(dig, dig, go_to("B3"))
    other = Script(
        {"action": "move", "direction": "east"},
        {"action": "move", "direction": "north"},
    )
    records = played([walker, other])
    assert records[3]["outcome"]["position"] == [1, 0]  # pirate-2 stands on B5
    # East comes first, but pirate-2 is there, so pirate-1 goes south.
    assert records[4]["go_to"] == "B3"
    assert records[4]["did"] == [{"action": "move", "direction": "south"}]


def test_go_to_that_can_t_start_fails_without_using_the_turn():
    # Off the island, its own square, and every shortest way blocked by pirate-2.
    walker = Script(go_to("Z9"), go_to("A5"), go_to("A1"), {"action": "dig"})
    records = played([walker, Script()], failed_tries=4)
    assert records[0]["did"] == [{"action": "dig"}]
    told = [view.turn_text() for view in walker.views[1:]]
    assert "There is no square Z9 on the island." in told[0]
    assert "You are already at A5." in told[1]
    assert "You can't go to A1: pirate-2 is in the way." in told[2]
    assert "go to Z9" in records[0]["story"]


def test_go_to_is_refused_while_it_is_off():
    walker = Script(go_to("E1"), {"action": "dig"})
    records = played([walker], go_to=False)
    assert records[0]["did"] == [{"action": "dig"}]
    assert "go_to isn't one of your tools in this game." in walker.views[1].turn_text()


def test_go_to_is_a_tool_and_a_rule_only_while_it_is_on():
    on, off = parse_config({"go_to": True}), parse_config({})
    assert "go_to" in system_prompt(on)
    assert "go_to" not in system_prompt(off)

    class Replies:
        sent = []

        def ask(self, request):
            self.sent.append(request)
            return json.dumps({"tool": "dig", "arguments": {}})

        last_retries = 0

    for config, offered in ((on, True), (off, False)):
        replies = Replies()
        brain = LLMPirate("pirate-1", config.pirates[0], replies, config)
        Game(config, [brain] + [Script()] * (config.crew_size - 1)).records().__next__()
        names = [tool["name"] for tool in replies.sent[-1]["tools"]]
        assert ("go_to" in names) is offered


def test_go_to_and_status_sheet_off_save_nothing(tmp_path):
    save_config(parse_config({}), tmp_path / "config.json")
    saved = json.loads((tmp_path / "config.json").read_text())
    assert "go_to" not in saved and "status_sheet" not in saved
    save_config(parse_config({"go_to": True, "status_sheet": True}), tmp_path / "on")
    saved = json.loads((tmp_path / "on").read_text())
    assert saved["go_to"] is True and saved["status_sheet"] is True


def test_status_sheet_starts_every_turn_text():
    brain = Script({"action": "dig"}, {"action": "move", "direction": "east"})
    seat = PirateSeat("pirate-1", brain, parse_config({"status_sheet": True}))
    seat.take_turn((0, 0), 30, (("south", "pirate-2"),))
    seat.remember("You dug here and found nothing.")
    seat.take_turn((0, 0), 29)
    seat.remember("You moved east.")
    seat.take_turn((1, 0), 28, (("east", "pirate-3"),))
    assert (
        brain.views[0]
        .turn_text()
        .startswith(
            "Status sheet:\n- Your square: A10\n- Turns left: 30 of 30, counting this one"
            "\n- Squares you dug: none yet\n- Crew seen beside you: pirate-2 at A9 on "
            "your turn 1\n\nYour earlier turns:\n"
        )
    )
    assert (
        brain.views[2]
        .turn_text()
        .startswith(
            "Status sheet:\n- Your square: B10\n- Turns left: 28 of 30, counting this one"
            "\n- Squares you dug: A10\n- Crew seen beside you: pirate-2 at A9 on your "
            "turn 1; pirate-3 at C10 on your turn 3\n\nYour earlier turns:\n"
        )
    )


def test_status_sheet_is_left_out_while_off():
    brain = Script()
    seat = PirateSeat("pirate-1", brain, parse_config({}))
    seat.take_turn((0, 0), 30)
    assert brain.views[0].turn_text().startswith("Your earlier turns:\n")
