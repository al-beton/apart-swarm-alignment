"""The scripted pirates: strategies that play the game and spend no tokens.

Each is a brain, like any other. Everything a strategy knows comes from its view
(its position and its own earlier turns), so it remembers nothing itself and a
game can't depend on anything else. The silent pirate is told the grid's size
when it's made, because that's in the rules a model reads as text.

`python -m treasure_island.strategies` remakes the committed reference games.

Implements: agents/model-per-pirate, treasure-island/silent, treasure-island/say-a-number, treasure-island/scribe, treasure-island/reference-games, treasure-island/no-token-strategies, treasure-island/brain-in-config
"""

from pathlib import Path

from treasure_island.brain import Decision, tool_call
from treasure_island.config import ConfigError, load_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import STEPS
from treasure_island.llm import LLMPirate


def _distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Silent:
    """Searches alone: digs what isn't dug, walks to the nearest square it hasn't
    seen dug, and goes into the cave once it stands on it. It never writes or reads.
    """

    def __init__(self, grid_size):
        self._size = grid_size
        # Ties go to the topmost square, then the leftmost (default, Al to confirm).
        self._squares = [(x, y) for y in range(grid_size) for x in range(grid_size)]

    def _nearest_unseen(self, square, seen):
        unseen = [other for other in self._squares if other not in seen]
        if not unseen:
            return None
        return min(unseen, key=lambda other: _distance(square, other))

    def decide(self, view):
        if view.on_cave:
            return Decision(
                tool_call("enter", {}), "This is the open cave, so I'm going in."
            )
        if not view.square_dug:
            return Decision(tool_call("dig", {}), "Nobody has dug this square yet.")
        # Every square it has stood on was dug by the time it left, as it digs
        # any it finds undug.
        seen = {turn.position for turn in view.earlier_turns} | {view.position}
        here = view.position
        target = self._nearest_unseen(here, seen)
        if target is None:
            return Decision(tool_call("dig", {}), "I've seen every square dug.")
        blockers = dict(view.neighbours)
        steps = {
            direction: (here[0] + step_x, here[1] + step_y)
            for direction, (step_x, step_y) in STEPS.items()
        }
        free = [
            direction
            for direction, (x, y) in steps.items()
            if 0 <= x < self._size and 0 <= y < self._size and direction not in blockers
        ]
        closer = [
            direction
            for direction in free
            if _distance(steps[direction], target) < _distance(here, target)
        ]
        where = f"({target[0]}, {target[1]})"
        if closer:
            why = f"The nearest square I haven't seen dug is {where}."
            return Decision(tool_call("move", {"direction": closer[0]}), why)
        in_way = " and ".join(
            name
            for direction, name in view.neighbours
            if _distance(steps[direction], target) < _distance(here, target)
        )
        if not free:
            why = f"{in_way or 'A pirate'} is in the way and I can't go round, so I dig here again."
            return Decision(tool_call("dig", {}), why)
        around = min(
            free,
            key=lambda direction: _distance(
                steps[direction], self._nearest_unseen(steps[direction], seen)
            ),
        )
        why = f"I'm heading for {where}, but {in_way} is in the way, so I go round."
        return Decision(tool_call("move", {"direction": around}), why)


class Scribe(Silent):
    """Searches like the silent pirate, but spends the turn after each dig writing
    what it found, and writes where the cave is before it goes in. It never reads.
    """

    def decide(self, view):
        last = view.earlier_turns[-1].action if view.earlier_turns else {}
        x, y = view.position
        if view.on_cave:
            # Walked onto or just opened, it says where the cave is, then goes in.
            if last.get("action") != "write":
                note = f"Treasure at ({x}, {y})"
                why = "I'm on the open cave, so I tell the crew where it is."
                return Decision(tool_call("write", {"text": note}), why)
            return super().decide(view)
        if last.get("action") == "dig":
            note = f"Dug ({x}, {y}): nothing"
            return Decision(tool_call("write", {"text": note}), "I write what I found.")
        return super().decide(view)


class SayANumber:
    """Writes the next number to the log each turn, and never digs."""

    def decide(self, view):
        number = len(view.earlier_turns) + 1
        return Decision(tool_call("write", {"text": str(number)}), "I just count.")


def brains_for(name, config, replies=None):
    """One fresh brain per pirate: its model's, through `replies`, else `name`'s."""
    known = {
        "silent": lambda: Silent(config.grid_size),
        "say-a-number": SayANumber,
        "scribe": lambda: Scribe(config.grid_size),
    }
    if name not in known:
        raise ConfigError(f"There's no brain '{name}': use one of {', '.join(known)}.")
    make = known[name]
    return [
        LLMPirate(f"pirate-{index + 1}", pirate.model, replies, config)
        if pirate.model
        else make()
        for index, pirate in enumerate(config.pirates)
    ]


REFERENCE_GAMES = ("silent", "say-a-number", "scribe")


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
