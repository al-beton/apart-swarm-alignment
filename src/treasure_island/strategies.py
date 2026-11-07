"""The scripted pirates: strategies that play the game and spend no tokens.

Each is a brain, like any other. Everything a strategy knows comes from its view
(its position and its own earlier turns), so it remembers nothing itself and a
game can't depend on anything else. The sweeper is told the grid's size when
it's made, because that's in the rules a model reads as text.

`python -m treasure_island.strategies` remakes the committed reference games.

Implements: agents/model-per-pirate, treasure-island/sweeper, treasure-island/stripes, treasure-island/reference-games, treasure-island/no-token-strategies, treasure-island/brain-in-config
"""

import re
from pathlib import Path

from treasure_island.brain import Decision, tool_call
from treasure_island.config import ConfigError, load_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import CAVE_HERE, TREASURE_FOUND
from treasure_island.llm import LLMPirate


def _s_shape(size):
    """Every square once: along the top row, back along the next, and so on."""
    return [
        (x if y % 2 == 0 else size - 1 - x, y) for y in range(size) for x in range(size)
    ]


def _step_towards(here, there):
    if there[0] != here[0]:
        return "east" if there[0] > here[0] else "west"
    return "south" if there[1] > here[1] else "north"


class Sweeper:
    """Digs each square along an S, and goes into the cave once it finds it."""

    def __init__(self, grid_size):
        self._squares = _s_shape(grid_size)

    def decide(self, view):
        earlier = view.earlier_turns
        if earlier and earlier[-1].result in (TREASURE_FOUND, CAVE_HERE):
            return Decision(
                tool_call("enter", {}), "This is the cave, so I'm going in."
            )
        dug = {turn.position for turn in earlier if turn.action["action"] == "dig"}
        if view.position not in dug:
            return Decision(tool_call("dig", {}), "I haven't dug this square yet.")
        # Some square is always left: digging them all would have found the treasure.
        x, y = next(square for square in self._squares if square not in dug)
        direction = _step_towards(view.position, (x, y))
        why = f"The next square to dig is ({x}, {y})."
        return Decision(tool_call("move", {"direction": direction}), why)


_NOTE = re.compile(r"The treasure is at \((\d+), (\d+)\)\.")
READS_EVERY = 5  # a striping pirate reads on its 5th, 10th, ... turn


def _note(square):
    return f"The treasure is at ({square[0]}, {square[1]})."


class Stripes:
    """Digs its own rows, says when it's blocked, and tells the crew where the cave is.

    Pirate n of a crew of k takes rows n, n+k, n+2k, ... (counting from 0), along
    the first one and back along the next. Default, Al to confirm: once its rows
    are done it reads every turn, waiting to hear where the cave is.
    """

    def __init__(self, grid_size, crew_size, index):
        rows = range(index, grid_size, crew_size)
        self._route = [
            (x if n % 2 == 0 else grid_size - 1 - x, y)
            for n, y in enumerate(rows)
            for x in range(grid_size)
        ]

    def decide(self, view):
        earlier = view.earlier_turns
        if about_the_cave := _for_the_cave(view, earlier):
            return about_the_cave
        if (len(earlier) + 1) % READS_EVERY == 0:
            return Decision(tool_call("read", {}), "Every 5th turn I read the scroll.")
        dug = {t.position for t in earlier if t.square_dug or _did(t, "dig")}
        if view.square_dug:
            dug.add(view.position)
        if view.position in self._route and view.position not in dug:
            return Decision(tool_call("dig", {}), "This square is on my rows.")
        target = next((square for square in self._route if square not in dug), None)
        if target is None:
            return Decision(
                tool_call("read", {}), "My rows are done, so I wait for news."
            )
        return _step(view, target, f"The next square on my rows is {target}.")


def _for_the_cave(view, earlier):
    """What to do about the cave: tell the crew, go in, or head there; else None."""
    opened = next((t.position for t in earlier if t.result == TREASURE_FOUND), None)
    if opened and not any(t.action == _write(_note(opened)) for t in earlier):
        return Decision(_write(_note(opened)), "I found it, so the crew should know.")
    cave = opened or _cave_known(earlier)
    if cave == view.position:
        return Decision(tool_call("enter", {}), "This is the cave, so I'm going in.")
    if cave:
        return _step(view, cave, f"The cave is at ({cave[0]}, {cave[1]}).")
    return None


def _write(text):
    return tool_call("write", {"text": text})


def _did(turn, action):
    return bool(turn.action) and turn.action["action"] == action


def _cave_known(earlier):
    """Where the cave is, if a dig or the scroll has said."""
    for turn in reversed(earlier):
        if turn.result == CAVE_HERE:
            return turn.position
        for line in turn.read_lines:
            if found := _NOTE.search(line["text"]):
                return int(found[1]), int(found[2])
    return None


def _step(view, target, why):
    """A move towards `target`, or a note that a pirate is in the way."""
    direction = _step_towards(view.position, target)
    if direction in dict(view.neighbours):
        return Decision(_write("I am blocked"), f"A pirate is in my way {direction}.")
    return Decision(tool_call("move", {"direction": direction}), why)


def brains_for(name, config, replies=None):
    """One fresh brain per pirate: its model's, through `replies`, else `name`'s."""
    known = {
        "s-sweep": lambda index: Sweeper(config.grid_size),
        "stripes": lambda index: Stripes(config.grid_size, config.crew_size, index),
    }
    if name not in known:
        raise ConfigError(f"There's no brain '{name}': use one of {', '.join(known)}.")
    make = known[name]
    return [
        LLMPirate(f"pirate-{index + 1}", pirate.model, replies, config)
        if pirate.model
        else make(index)
        for index, pirate in enumerate(config.pirates)
    ]


REFERENCE_GAMES = ("s-sweep", "stripes")


def write_reference(name, folder, root=Path()):
    """Play a reference game from its config in `root` into `folder`."""
    config = load_config(Path(root) / "configs" / f"{name}.toml")
    save_config(config, Path(folder) / "config.json")
    write_game(config, brains_for(config.brain, config), folder)


def main():
    for name in REFERENCE_GAMES:
        folder = Path("runs") / f"reference-{name}"
        folder.mkdir(parents=True, exist_ok=True)
        write_reference(name, folder)
        print(folder)


if __name__ == "__main__":
    main()
