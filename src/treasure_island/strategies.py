"""The scripted pirates: strategies that play the game and spend no tokens.

Each is a brain, like any other. Everything a strategy knows comes from its view
(its position and its own earlier turns), so it remembers nothing itself and a
game can't depend on anything else. Each is told the grid's size when it's made,
because that's in the rules a model reads as text, and a striping pirate is also
told its place in the crew, as a model can read from its name.

`python -m treasure_island.strategies` remakes the committed reference games.

Implements: treasure-island/pool, agents/reasoning-looked-up, agents/model-per-pirate, treasure-island/silent, treasure-island/stripes, treasure-island/scribe, treasure-island/reference-games, treasure-island/no-token-strategies, treasure-island/brain-in-config, treasure-island/square-names
"""

import re
from pathlib import Path

from treasure_island.brain import Decision, tool_call
from treasure_island.config import ConfigError, load_config, save_config
from treasure_island.game_loop import write_game
from treasure_island.game_state import STEPS, TREASURE_FOUND
from treasure_island.llm import LLMPirate
from treasure_island.squares import square_at, square_name


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
        where = square_name(target, self._size)
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


_NOTE = re.compile(r"The treasure is at ([A-Z]\d+)\.")
READS_EVERY = 5  # a striping pirate reads on its 5th, 10th, ... turn


def _note(square, grid_size):
    return f"The treasure is at {square_name(square, grid_size)}."


class Stripes:
    """Digs its own rows, says when it's blocked, and tells the crew where the cave is.

    Pirate n of a crew of k takes rows n, n+k, n+2k, ... (counting from 0), along
    the first one and back along the next. Default, Al to confirm: once its rows
    are done it reads every turn, waiting to hear where the cave is.
    """

    def __init__(self, grid_size, crew_size, index):
        self._size = grid_size
        rows = range(index, grid_size, crew_size)
        self._route = [
            (x if n % 2 == 0 else grid_size - 1 - x, y)
            for n, y in enumerate(rows)
            for x in range(grid_size)
        ]

    def decide(self, view):
        earlier = view.earlier_turns
        if about_the_cave := _for_the_cave(view, earlier, self._size):
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
        where = square_name(target, self._size)
        return _step(view, target, f"The next square on my rows is {where}.")


class Scribe(Silent):
    """Searches like the silent pirate, but spends the turn after each dig writing
    what it found, and writes where the cave is before it goes in. It never reads.
    """

    def decide(self, view):
        last = view.earlier_turns[-1].action if view.earlier_turns else {}
        here = square_name(view.position, self._size)
        if view.on_cave:
            # Walked onto or just opened, it says where the cave is, then goes in.
            if last.get("action") != "write":
                note = f"Treasure at {here}"
                why = "I'm on the open cave, so I tell the crew where it is."
                return Decision(tool_call("write", {"text": note}), why)
            return super().decide(view)
        if last.get("action") == "dig":
            note = f"Dug {here}: nothing"
            return Decision(tool_call("write", {"text": note}), "I write what I found.")
        return super().decide(view)


_READING = re.compile(r"Your rod reads about (\d+) squares from the cave\.")
_POOLED = re.compile(r"Rod at ([A-Z]\d+) reads (\d+)\.")


class Pool:
    """Pools rod readings (`distance-reading`): after each missed dig it writes the
    reading on the scroll, it reads the scroll every few turns, and it digs only
    the squares every reading it knows of allows, nearest first. Like a striping
    pirate it tells the crew where the cave is and heads for it once told.
    """

    def __init__(self, grid_size, noise):
        self._size, self._noise = grid_size, noise
        self._squares = [(x, y) for y in range(grid_size) for x in range(grid_size)]

    def _readings(self, earlier):
        """Every (square, reading) it knows: its own digs' and the scroll's."""
        known = []
        for turn in earlier:
            if own := _READING.search(turn.result):
                known.append((turn.position, int(own[1])))
            for line in turn.read_lines:
                for square, reading in _POOLED.findall(line["text"]):
                    known.append((square_at(square, self._size), int(reading)))
        return known

    def _allowed(self, square, readings):
        return all(
            abs(_king(square, dug) - reading) <= self._noise
            or (reading == 0 and _king(square, dug) <= self._noise)
            for dug, reading in readings
        )

    def decide(self, view):
        earlier = view.earlier_turns
        if about_the_cave := _for_the_cave(view, earlier, self._size):
            return about_the_cave
        last = earlier[-1] if earlier else None
        if last and (own := _READING.search(last.result)):
            where = square_name(last.position, self._size)
            return Decision(_write(f"Rod at {where} reads {own[1]}."), "I share it.")
        if len(earlier) % POOL_READS_EVERY == POOL_READS_EVERY - 1:
            return Decision(tool_call("read", {}), "I catch up on the crew's rods.")
        readings = self._readings(earlier)
        dug = {square for square, _ in readings} | {
            t.position for t in earlier if t.square_dug or _did(t, "dig")
        }
        if view.square_dug:
            dug.add(view.position)
        here = view.position
        allowed = [
            s for s in self._squares if s not in dug and self._allowed(s, readings)
        ]
        if here in allowed:
            return Decision(tool_call("dig", {}), "The rods allow this square.")
        if not allowed:
            return Decision(
                tool_call("read", {}), "No square fits, so I wait for news."
            )
        target = min(allowed, key=lambda s: _distance(here, s))
        where = square_name(target, self._size)
        return _step(view, target, f"The nearest square the rods allow is {where}.")


POOL_READS_EVERY = 3  # a pooling pirate reads on its 3rd, 6th, ... turn


def _king(a, b):
    """Steps between two squares in king's moves, as the rod counts them."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _for_the_cave(view, earlier, size):
    """What to do about the cave: tell the crew, go in, or head there; else None."""
    opened = next((t.position for t in earlier if t.result == TREASURE_FOUND), None)
    if opened and not any(t.action == _write(_note(opened, size)) for t in earlier):
        note = _write(_note(opened, size))
        return Decision(note, "I found it, so the crew should know.")
    cave = opened or _cave_known(earlier, size)
    if view.on_cave or cave == view.position:
        return Decision(tool_call("enter", {}), "This is the cave, so I'm going in.")
    if cave:
        return _step(view, cave, f"The cave is at {square_name(cave, size)}.")
    return None


def _write(text):
    return tool_call("write", {"text": text})


def _did(turn, action):
    return bool(turn.action) and turn.action["action"] == action


def _cave_known(earlier, grid_size):
    """Where the cave is, if a dig or the scroll has said."""
    for turn in reversed(earlier):
        for line in turn.read_lines:
            if found := _NOTE.search(line["text"]):
                return square_at(found[1], grid_size)
    return None


def _step(view, target, why):
    """A move towards `target`, or a note that a pirate is in the way."""
    direction = _towards(view.position, target)
    if direction in dict(view.neighbours):
        return Decision(_write("I am blocked"), f"A pirate is in my way {direction}.")
    return Decision(tool_call("move", {"direction": direction}), why)


def _towards(here, there):
    """The way to step from `here` towards `there`: along the row first."""
    if there[0] != here[0]:
        return "east" if there[0] > here[0] else "west"
    return "south" if there[1] > here[1] else "north"


def brains_for(name, config, replies=None):
    """One fresh brain per pirate: its model's, through `replies`, else `name`'s."""
    known = {
        "silent": lambda index: Silent(config.grid_size),
        "stripes": lambda index: Stripes(config.grid_size, config.crew_size, index),
        "scribe": lambda index: Scribe(config.grid_size),
        "pool": lambda index: Pool(config.grid_size, config.distance_noise or 0),
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


REFERENCE_GAMES = ("silent", "stripes", "scribe", "pool")


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
