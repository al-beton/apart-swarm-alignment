"""The scripted pirates: strategies that play the real game and spend no tokens.

Each is a brain, like any other. Everything a strategy knows comes from its view
(its position and its own earlier turns), so it remembers nothing itself and a
game can't depend on anything else. The sweeper is told the grid's size when
it's made, because that's in the rules a model reads as text.

`python -m treasure_island.strategies` remakes the committed reference games.

Implements: treasure-island/sweeper, treasure-island/say-a-number, treasure-island/reference-games, treasure-island/no-token-strategies, treasure-island/brain-in-config
"""

from pathlib import Path

from treasure_island.brain import Decision, tool_call
from treasure_island.config import ConfigError, load_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import TREASURE_FOUND


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
    """Digs each square along an S, and stays on the treasure once it finds it."""

    def __init__(self, grid_size):
        self._squares = _s_shape(grid_size)

    def decide(self, view):
        earlier = view.earlier_turns
        if any(turn.result == TREASURE_FOUND for turn in earlier):
            return Decision(tool_call("dig", {}), "I found it, so I'm staying here.")
        dug = {turn.position for turn in earlier if turn.action["action"] == "dig"}
        if view.position not in dug:
            return Decision(tool_call("dig", {}), "I haven't dug this square yet.")
        # Some square is always left: digging them all would have found the treasure.
        x, y = next(square for square in self._squares if square not in dug)
        direction = _step_towards(view.position, (x, y))
        why = f"The next square to dig is ({x}, {y})."
        return Decision(tool_call("move", {"direction": direction}), why)


class SayANumber:
    """Writes the next number to the log each turn, and never digs."""

    def decide(self, view):
        number = len(view.earlier_turns) + 1
        return Decision(tool_call("write", {"text": str(number)}), "I just count.")


def brains_for(name, config):
    """One fresh brain per pirate, all playing the same strategy."""
    known = {
        "s-sweep": lambda: Sweeper(config.grid_size),
        "say-a-number": SayANumber,
    }
    if name not in known:
        raise ConfigError(f"There's no brain '{name}': use one of {', '.join(known)}.")
    make = known[name]
    return [make() for _ in range(config.crew_size)]


REFERENCE_GAMES = ("s-sweep", "say-a-number")


def write_reference(name, folder, root=Path()):
    """Play a reference game from its config in `root` into `folder`."""
    config = load_config(Path(root) / "configs" / f"{name}.toml")
    write_game(config, brains_for(config.brain, config), folder)


def main():
    for name in REFERENCE_GAMES:
        folder = Path("runs") / f"reference-{name}"
        folder.mkdir(parents=True, exist_ok=True)
        write_reference(name, folder)
        print(folder)


if __name__ == "__main__":
    main()
