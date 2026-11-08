"""The scripted pirates: strategies that play the game and spend no tokens.

Each is a brain, like any other. Everything a strategy knows comes from its view
(its square, its readings, the scroll lines it is shown and its own earlier
turns), so it remembers nothing itself and a game can't depend on anything
else. Each is told the grid's size when it's made, because that's in the rules
a model reads as text.

`python -m treasure_island.strategies` remakes the committed reference games.

The loner and the sharer also triangulate: each keeps the squares its readings
allow (`possible`), and the sharer counts the readings shared on the scroll too.
Each is told `reading_noise` as well, since the rules say how far off a reading
can be.

Implements: agents/reasoning-looked-up, agents/model-per-pirate, treasure-island/silent, treasure-island/loner, treasure-island/sharer, treasure-island/reference-games, treasure-island/no-token-strategies, treasure-island/brain-in-config, treasure-island/square-names
"""

import re
from pathlib import Path

from treasure_island.brain import Decision, tool_call
from treasure_island.config import ConfigError, load_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import distance, first_step
from treasure_island.llm import LLMPirate
from treasure_island.squares import square_at, square_name


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


def allows(dug, away, square, noise=0):
    """Whether a reading of `away` got at `dug` leaves the treasure on `square`.

    A reading is the true distance off by up to `noise` either way but never
    below 1, so a reading of 1 allows every square up to 1 + `noise` away. The
    dug square itself never holds the treasure: digging it would have found it.
    """
    true = distance(dug, square)
    if true == 0:
        return False
    if away <= 1:
        return true <= 1 + noise
    return abs(true - away) <= noise


def possible(grid_size, noise, readings, ruled_out=()):
    """Every square every (square, away) reading allows and isn't ruled out.

    They come topmost first, then leftmost, which is how ties are broken.
    """
    ruled_out = set(ruled_out)
    return [
        (x, y)
        for y in range(grid_size)
        for x in range(grid_size)
        if (x, y) not in ruled_out
        and all(allows(dug, away, (x, y), noise) for dug, away in readings)
    ]


CAVE_LINE = re.compile(r"Cave at ([A-Z]\d+)\.")


def cave_said(lines, grid_size):
    """The square the first line in the sharer's form "Cave at C4." names, or None.

    Any other line, or a square that isn't on the island, is passed over.
    """
    for line in lines:
        if found := CAVE_LINE.fullmatch(line["text"]):
            return square_at(found[1], grid_size)
    return None


def shared(readings, grid_size):
    """The (square, away) of each (by, square's name, away) shared reading."""
    return [(square_at(name, grid_size), away) for _, name, away in readings]


class Loner(Silent):
    """Triangulates from its own readings: goes for the nearest square they allow.

    It digs the square it stands on whenever it isn't dug, since the reading is
    free news, unless the readings already leave one square and it's elsewhere;
    otherwise it goes to the nearest square they allow that it hasn't seen dug.
    It is asked only where it starts, arrives or is stopped, so it never digs on
    the way. It never says anything and enters the cave once it stands on it.
    """

    def __init__(self, grid_size, noise=0):
        super().__init__(grid_size)
        self._noise = noise

    def _known(self, view):
        """The (square, away) readings it counts, the squares ruled out, the cave."""
        readings = [(r.position, r.away) for r in view.readings if r.away is not None]
        return readings, self._seen_dug(view), None

    def _line(self, view):
        """The line to say with this turn's action, and whether it's an alert."""
        return None, False

    def _act(self, view, name, arguments, why):
        """A tool call with this turn's line, if there is one."""
        line, alert = self._line(view)
        if line:
            arguments = {**(arguments or {}), "say": line, "alert": alert}
        return Decision(tool_call(name, arguments), why)

    def decide(self, view):
        if view.on_cave:
            return self._act(view, "enter", None, "This is the open cave, so I go in.")
        readings, ruled_out, cave = self._known(view)
        if cave is not None:
            return self._head_for(view, [cave], "The cave is at {}, so I go there.")
        keep = possible(self._size, self._noise, readings, ruled_out)
        if not view.square_dug and view.position in keep:
            return self._act(view, "dig", None, "The treasure could be right here.")
        if not view.square_dug and len(keep) != 1:
            # A reading is free news wherever it's taken, so it digs before going
            # on, unless the readings already leave one square and it's elsewhere.
            why = "It can't be here, but nobody has dug it, so its reading is news."
            return self._act(view, "dig", None, why)
        if not keep:  # only readings that disagree with the rules could leave none
            keep = [square for square in self._squares if square not in ruled_out]
        why = "The nearest square the readings allow is {}."
        return self._head_for(view, keep, why)

    def _head_for(self, view, targets, why):
        """Go to the nearest target whose way is free, else step aside, else wait."""
        here, blocked = view.position, dict(view.neighbours)
        targets = sorted(
            (target for target in targets if target != here),
            key=lambda target: distance(here, target),
        )
        for target in targets:
            if first_step(here, target) not in blocked:
                where = square_name(target, self._size)
                return self._act(view, "go_to", {"square": where}, why.format(where))
        if targets and targets[0][0] != here[0] and targets[0][1] != here[1]:
            # The row is blocked, so take the column's step first, if it's free.
            aside = (here[0], here[1] + (1 if targets[0][1] > here[1] else -1))
            if first_step(here, aside) not in blocked:
                where = square_name(aside, self._size)
                return self._act(
                    view, "go_to", {"square": where}, "A pirate is in my way."
                )
        return self._act(view, "wait", None, "Pirates block my way, so I wait.")


class Sharer(Loner):
    """Plays like the loner, counting every reading shared on the scroll as well.

    It digs with `share` set, so each reading reaches the scroll as it gets it,
    never digs a square shared as dug, says "Cave at C4." as an alert when it
    dug up the cave and goes in, and once it is shown where the cave is it goes
    there. Readings it takes only from shared lines, never from what a line says.
    """

    def _known(self, view):
        readings, ruled_out, _ = super()._known(view)
        heard = shared(view.shared_readings, self._size)
        readings += heard
        ruled_out |= {square for square, _ in heard}
        lines = [line for turn in view.earlier_turns for line in turn.shown]
        return readings, ruled_out, cave_said([*lines, *view.new_lines], self._size)

    def _act(self, view, name, arguments, why):
        if name == "dig":
            arguments = {**(arguments or {}), "share": True}
        return super()._act(view, name, arguments, why)

    def _line(self, view):
        if view.on_cave and any(r.away is None for r in view.readings):
            return f"Cave at {view.square}.", True
        return None, False


def brains_for(name, config, replies=None):
    """One fresh brain per pirate: its model's, through `replies`, else `name`'s."""
    known = {
        "silent": lambda index: Silent(config.grid_size),
        "loner": lambda index: Loner(config.grid_size, config.reading_noise),
        "sharer": lambda index: Sharer(config.grid_size, config.reading_noise),
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


REFERENCE_GAMES = ("silent", "loner", "sharer")


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
