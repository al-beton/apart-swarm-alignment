# Implements: treasure-island/say-on-any-action, treasure-island/alert, treasure-island/shown-when-asked
"""A talking game for the tests: a scripted crew that says what each dig found.

Until the sharer is built, no committed scripted crew talks, so the tests that
need a finished game with lines on the scroll, thinking and pirates going into
the cave play this one into a folder of their own. Each pirate searches like the
silent pirate, says every reading it gets, says where the cave is as an alert
when it digs it up and goes in, and goes to the cave once it is shown where.
"""

import re

from treasure_island.brain import Decision, tool_call
from treasure_island.config import parse_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import first_step
from treasure_island.squares import square_at
from treasure_island.strategies import Silent

CAVE = re.compile(r"Cave at ([A-Z]\d+)\.")
SETTINGS = {"grid_size": 5, "crew_size": 3, "turns_per_pirate": 20, "seed": 7}


class Talker(Silent):
    def decide(self, view):
        heard = [line for turn in view.earlier_turns for line in turn.shown]
        heard += list(view.new_lines)
        named = [found[1] for line in heard if (found := CAVE.search(line["text"]))]
        if view.on_cave:
            enter = tool_call(
                "enter", {"say": f"Cave at {view.square}.", "alert": True}
            )
            return Decision(enter, "This is the cave: I say where it is and go in.")
        if named and square_at(named[0], self._size) != view.position:
            there = square_at(named[0], self._size)
            if first_step(view.position, there) in dict(view.neighbours):
                return Decision(tool_call("wait"), "A pirate is in my way to the cave.")
            order = tool_call("go_to", {"square": named[0]})
            return Decision(order, f"The cave is at {named[0]}, so I go there.")
        decision = super().decide(view)
        last = view.earlier_turns[-1] if view.earlier_turns else None
        if last and last.action and last.action["action"] == "dig" and view.readings:
            reading = view.readings[-1]
            if reading.away is not None:
                line = f"Dug {reading.square}: {reading.away} away."
                return Decision({**decision.action, "say": line}, decision.thinking)
        return decision


def config(**settings):
    return parse_config({**SETTINGS, **settings})


def write(folder, **settings):
    """Play the talking game into `folder`, with its config, and return the folder."""
    folder.mkdir(parents=True, exist_ok=True)
    game = config(**settings)
    save_config(game, folder / "config.json")
    write_game(game, [Talker(game.grid_size) for _ in game.pirates], folder)
    return folder
