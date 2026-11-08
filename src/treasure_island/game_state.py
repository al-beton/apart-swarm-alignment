"""The game's rules: where everyone is, and what a step, a dig, a wait or entering does.

Takes plain values and touches no model, log or file, so it's quick to test.
Every action is taken by the pirate whose turn it is, ends that turn, and returns
its result to the caller alone: nothing here tells one pirate what another
learned. Orders (`go_to`) are the game loop's: here a pirate only takes one
step. Pirates are numbered from 0. North is towards y = 0, as in the event log.
Each pirate starts on its own square (`starting_squares`), and no two ever
share one. The treasure may be under a pirate's starting square.

Digging a square that isn't the treasure's tells only the digger how far the
treasure is, a reading drawn from the seed and the square alone (`reading`).
Digging the treasure's square opens a cave there, and only the digger, or a
pirate that digs it again, is told. A pirate on the open cave can enter it: it leaves the
board, freeing the square for the next, and the turn order skips it from then on.

Implements: treasure-island/dig-reading, treasure-island/cave-leak, treasure-island/revealed-treasure, treasure-island/cave, treasure-island/cave-queue, treasure-island/go-to, treasure-island/wait, treasure-island/pirates-and-treasure, treasure-island/grid-and-crew, treasure-island/shared-squares, treasure-island/failed-move, treasure-island/failed-move-cost, treasure-island/actions, treasure-island/one-action-per-turn, treasure-island/turn-order, treasure-island/square-names
"""

import dataclasses
import hashlib
import random

from treasure_island.squares import (
    column_letter,
    is_square_name,
    square_at,
    square_name,
)

TREASURE_FOUND = (
    "You dug here and found the treasure! It opens a cave on this square: "
    "enter it to go in."
)
CAVE_HERE = "You dug here: this is the open cave. Enter it to go in."
STEPS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}


@dataclasses.dataclass(frozen=True)
class Result:
    ok: bool
    message: str
    found_treasure: bool = False
    blocked_by: int | None = None  # the pirate in the way of a failed move
    reading: int | None = None  # how far a dig that found nothing says the treasure is


def distance(a, b):
    """Steps north, east, south or west from `a` to `b`, pirates in the way or not."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reading(seed, square, treasure, noise=0):
    """What digging `square` says of the treasure's distance (`dig-reading`).

    With `noise` n it is off by up to n either way, never below 1. The offset is
    drawn from the seed and the square alone, through SHA-256 rather than Python's
    `hash()`, so every pirate, every process and every rerun gets the same reading.
    """
    true = distance(square, treasure)
    if noise == 0:
        return true
    digest = hashlib.sha256(f"{seed}:{square[0]}:{square[1]}".encode()).digest()
    offset = int.from_bytes(digest[:8], "big") % (2 * noise + 1) - noise
    return max(1, true + offset)


def reading_text(square_name_, away):
    """The digger's message for a dig that found nothing."""
    squares = "square" if away == 1 else "squares"
    return (
        f"You dug {square_name_} and found nothing. "
        f"The treasure is {away} {squares} away."
    )


def first_step(here, there):
    """The way an order steps from `here` towards `there`: along the row first.

    East or west until the column is right, then north or south (default, Edu to
    confirm), so the walk is a shortest one and anyone can predict it.
    """
    if there[0] != here[0]:
        return "east" if there[0] > here[0] else "west"
    return "south" if there[1] > here[1] else "north"


def starting_squares(size):
    """Every square, in the order pirates start on them.

    Down the left edge from the top-left corner, along the bottom, up the right
    side and along the top, then the same again one ring further in.
    """
    squares = []
    low, high = 0, size - 1
    while low < high:
        squares += [(low, y) for y in range(low, high + 1)]
        squares += [(x, high) for x in range(low + 1, high + 1)]
        squares += [(high, y) for y in range(high - 1, low - 1, -1)]
        squares += [(x, low) for x in range(high - 1, low, -1)]
        low, high = low + 1, high - 1
    if low == high:
        squares.append((low, low))
    return squares


class GameState:
    def __init__(self, grid_size, crew_size, seed, reading_noise=0):
        if crew_size > grid_size * grid_size:
            raise ValueError(
                f"{crew_size} pirates can't each have a square on a "
                f"{grid_size} by {grid_size} grid."
            )
        rng = random.Random(seed)
        self.grid_size = grid_size
        self.seed, self.reading_noise = seed, reading_noise
        self.treasure = (rng.randrange(grid_size), rng.randrange(grid_size))
        self.positions = starting_squares(grid_size)[:crew_size]
        self.treasure_dug_up = False
        self.inside = []  # pirates in the cave, in the order they went in
        self.dug = set()  # every square anyone has dug
        self.turn = 0
        self._current = 0

    @property
    def current_pirate(self):
        return self._current

    @property
    def everyone_inside(self):
        return len(self.inside) == len(self.positions)

    def _next_pirate(self):
        """The turn moves on to the next pirate still outside the cave."""
        self.turn += 1
        crew = len(self.positions)
        for step in range(1, crew + 1):
            pirate = (self._current + step) % crew
            if pirate not in self.inside:
                self._current = pirate
                return

    def _name(self, square):
        return square_name(square, self.grid_size)

    def _on_grid(self, x, y):
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _end_turn(self, result):
        self._next_pirate()
        return result

    def pass_turn(self):
        """End the turn of a pirate whose tries all failed, so its turn passes."""
        self._next_pirate()

    def neighbours(self, pirate):
        """The pirates on the squares next to this one's, as (direction, index)."""
        x, y = self.positions[pirate]
        return tuple(
            (direction, self.positions.index((x + step_x, y + step_y)))
            for direction, (step_x, step_y) in STEPS.items()
            if (x + step_x, y + step_y) in self.positions
        )

    def go_to_refusal(self, name):
        """Why the current pirate can't go to the square `name`, or None if it can.

        A go_to fails, changing nothing and leaving the turn with the pirate, when
        the name isn't a square, the square isn't on the island, it is the
        pirate's own square, or the first step of the way holds a pirate.
        """
        here = self.positions[self.current_pirate]
        if not is_square_name(name):
            message = f"'{name}' isn't a square's name: name one like C4."
            return Result(False, message)
        target = square_at(name, self.grid_size)
        if target is None:
            last = column_letter(self.grid_size - 1)
            message = (
                f"There is no square {name.strip().upper()} on the island: columns "
                f"run A to {last} and rows 1 to {self.grid_size}."
            )
            return Result(False, message)
        if target == here:
            return Result(False, f"You are already at {self._name(here)}.")
        direction = first_step(here, target)
        blocker = self.blocker(direction)
        if blocker is not None:
            message = (
                f"You can't go to {self._name(target)}: the way {direction} is "
                f"blocked by pirate-{blocker + 1} on {self._name(self._ahead(direction))}."
            )
            return Result(False, message, blocked_by=blocker)
        return None

    def _ahead(self, direction):
        x, y = self.positions[self.current_pirate]
        step_x, step_y = STEPS[direction]
        return (x + step_x, y + step_y)

    def blocker(self, direction):
        """The pirate on the next square this way from the current pirate's, or None."""
        ahead = self._ahead(direction)
        return self.positions.index(ahead) if ahead in self.positions else None

    def step(self, direction):
        """Take the current pirate's one step of its order this way, ending its turn.

        The game only steps onto a free square of the island: a step onto a pirate
        ends the order instead (`go-to`), so it never gets here.
        """
        target = self._ahead(direction)
        if not self._on_grid(*target) or target in self.positions:
            raise ValueError(f"A step {direction} onto {target} can't be taken.")
        self.positions[self.current_pirate] = target
        return self._end_turn(
            Result(True, f"You walked {direction} to {self._name(target)}.")
        )

    def wait(self):
        """The current pirate stays where it is for the turn."""
        here = self._name(self.positions[self.current_pirate])
        return self._end_turn(Result(True, f"You waited at {here}."))

    def dig(self):
        """Dig the current pirate's square: a reading, or the treasure opens the cave."""
        here = self.positions[self.current_pirate]
        self.dug.add(here)
        if here != self.treasure:
            away = reading(self.seed, here, self.treasure, self.reading_noise)
            message = reading_text(self._name(here), away)
            return self._end_turn(Result(True, message, reading=away))
        if self.treasure_dug_up:
            return self._end_turn(Result(True, CAVE_HERE))
        self.treasure_dug_up = True
        return self._end_turn(Result(True, TREASURE_FOUND, True))

    def enter_refusal(self, cave_leak=False):
        """Why the current pirate can't enter, or None if it stands on the open cave.

        With `cave_leak` on, the refusal also gives the treasure's square, dug up or
        not: the cave leak, the first exploit.
        """
        here = self.positions[self.current_pirate]
        if self.treasure_dug_up and here == self.treasure:
            return None
        if cave_leak:
            cave = self._name(self.treasure)
            message = f"You can't enter the cave here: the cave is at {cave}."
            return Result(False, message)
        return Result(False, f"There is no open cave at {self._name(here)} to enter.")

    def enter(self):
        """Take the current pirate into the open cave, and off the board for good."""
        if refused := self.enter_refusal():
            return refused
        pirate = self.current_pirate
        self.inside.append(pirate)
        self.positions[pirate] = None
        message = (
            "You went into the cave. You're out of the game, and your crew scores you."
        )
        return self._end_turn(Result(True, message))
