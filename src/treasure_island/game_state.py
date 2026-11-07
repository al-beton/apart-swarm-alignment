"""The game's rules: where everyone is, and what a move or a dig does.

Takes plain values and touches no model, log or file, so it's quick to test.
Every action is taken by the pirate whose turn it is, ends that turn, and returns
its result to the caller alone: nothing here tells one pirate what another
learned. Pirates are numbered from 0. North is towards y = 0, as in the event
log. Each pirate starts on its own square (`starting_squares`), and no two ever
share one. The treasure may be under a pirate's starting square.

Implements: treasure-island/pirates-and-treasure, treasure-island/grid-and-crew, treasure-island/shared-squares, treasure-island/failed-move, treasure-island/failed-move-cost, treasure-island/actions, treasure-island/one-action-per-turn, treasure-island/turn-order
"""

import dataclasses
import random

TREASURE_FOUND = "You dug here and found the treasure!"
STEPS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}


@dataclasses.dataclass(frozen=True)
class Result:
    ok: bool
    message: str
    found_treasure: bool = False
    blocked_by: int | None = None  # the pirate in the way of a failed move


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
    def __init__(self, grid_size, crew_size, seed):
        if crew_size > grid_size * grid_size:
            raise ValueError(
                f"{crew_size} pirates can't each have a square on a "
                f"{grid_size} by {grid_size} grid."
            )
        rng = random.Random(seed)
        self.grid_size = grid_size
        self.treasure = (rng.randrange(grid_size), rng.randrange(grid_size))
        self.positions = starting_squares(grid_size)[:crew_size]
        self.treasure_dug_up = False
        self.dug = set()  # every square anyone has dug
        self.turn = 0

    @property
    def current_pirate(self):
        return self.turn % len(self.positions)

    def _on_grid(self, x, y):
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _end_turn(self, result):
        self.turn += 1
        return result

    def pass_turn(self):
        """End the turn of a pirate who acted elsewhere, as writing or reading do."""
        self.turn += 1

    def neighbours(self, pirate):
        """The pirates on the squares next to this one's, as (direction, index)."""
        x, y = self.positions[pirate]
        return tuple(
            (direction, self.positions.index((x + step_x, y + step_y)))
            for direction, (step_x, step_y) in STEPS.items()
            if (x + step_x, y + step_y) in self.positions
        )

    def refusal(self, direction):
        """Why the current pirate can't move this way, or None if it can.

        A refused move changes nothing and doesn't end the turn, so the pirate
        can choose again.
        """
        if direction not in STEPS:
            known = ", ".join(STEPS)
            return Result(
                False, f"There is no direction '{direction}': use one of {known}."
            )
        x, y = self.positions[self.current_pirate]
        step_x, step_y = STEPS[direction]
        target = (x + step_x, y + step_y)
        if not self._on_grid(*target):
            message = f"You can't move {direction}: ({x}, {y}) is at the grid's edge."
            return Result(False, message)
        if target in self.positions:
            message = (
                f"You can't move {direction}: another pirate is standing on "
                f"({target[0]}, {target[1]})."
            )
            return Result(False, message, blocked_by=self.positions.index(target))
        return None

    def move(self, direction):
        """Move the current pirate one square, onto a free square on the grid.

        A move that can't happen is refused, and the turn stays with the pirate.
        """
        if refused := self.refusal(direction):
            return refused
        x, y = self.positions[self.current_pirate]
        step_x, step_y = STEPS[direction]
        target = (x + step_x, y + step_y)
        self.positions[self.current_pirate] = target
        message = f"You moved {direction} to ({target[0]}, {target[1]})."
        return self._end_turn(Result(True, message))

    def dig(self):
        """Dig the current pirate's square. Once dug up, the treasure stays dug up."""
        self.dug.add(self.positions[self.current_pirate])
        if self.positions[self.current_pirate] != self.treasure:
            return self._end_turn(Result(True, "You dug here and found nothing."))
        self.treasure_dug_up = True
        return self._end_turn(Result(True, TREASURE_FOUND, True))
