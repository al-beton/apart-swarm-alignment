"""The scripted pirates: strategies that play the game and spend no tokens.

Each is a brain, like any other. Everything a strategy knows comes from its view
(its square, its readings, the scroll lines it is shown and its own earlier
turns), so it remembers nothing itself and a game can't depend on anything
else. Each is told the grid's size when it's made, because that's in the rules
a model reads as text.

`python -m treasure_island.strategies` remakes the committed reference games.

Implements: agents/reasoning-looked-up, agents/model-per-pirate, treasure-island/silent, treasure-island/reference-games, treasure-island/no-token-strategies, treasure-island/brain-in-config, treasure-island/square-names
"""

from pathlib import Path

from treasure_island.brain import Decision, tool_call
from treasure_island.config import ConfigError, load_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import distance, first_step
from treasure_island.llm import LLMPirate
from treasure_island.squares import square_name


class Silent:
    """Searches alone and ignores readings: digs its square if it isn't dug, goes
    to the nearest square it hasn't seen dug, and goes into the cave once it
    stands on it. It never says anything.
    """

    def __init__(self, grid_size):
        self._size = grid_size
        # Ties go to the topmost square, then the leftmost.
        self._squares = [(x, y) for y in range(grid_size) for x in range(grid_size)]

    def _seen_dug(self, view):
        """Every square it has dug, or been told was dug when it stood there."""
        seen = {reading.position for reading in view.readings}
        seen |= {turn.position for turn in view.earlier_turns if turn.square_dug}
        if view.square_dug:
            seen.add(view.position)
        return seen

    def decide(self, view):
        if view.on_cave:
            return Decision(
                tool_call("enter"), "This is the open cave, so I'm going in."
            )
        if not view.square_dug:
            return Decision(tool_call("dig"), "Nobody has dug this square yet.")
        here, seen = view.position, self._seen_dug(view)
        blocked = dict(view.neighbours)
        unseen = sorted(
            (other for other in self._squares if other not in seen),
            key=lambda other: distance(here, other),
        )
        for target in unseen:
            way = first_step(here, target)
            where = square_name(target, self._size)
            if way not in blocked:
                why = f"The nearest square I haven't seen dug is {where}."
                return Decision(tool_call("go_to", {"square": where}), why)
        if unseen:
            return Decision(tool_call("wait"), "Pirates block every way I could go.")
        return Decision(tool_call("wait"), "I've seen every square dug.")


def brains_for(name, config, replies=None):
    """One fresh brain per pirate: its model's, through `replies`, else `name`'s."""
    known = {
        "silent": lambda index: Silent(config.grid_size),
    }
    if name not in known:
        raise ConfigError(f"There's no brain '{name}': use one of {', '.join(known)}.")
    make = known[name]
    return [
        LLMPirate(f"pirate-{index + 1}", pirate, replies, config)
        if pirate.model
        else make(index)
        for index, pirate in enumerate(config.pirates)
    ]


REFERENCE_GAMES = ("silent",)


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
