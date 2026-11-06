"""The game's rules: where everyone is, and what a move or a dig does.

Takes plain values and touches no model, log or file, so it's quick to test.
Every action is taken by the pirate whose turn it is, ends that turn, and returns
its result to the caller alone: nothing here tells one pirate what another
learned. Pirates are numbered from 0. North is towards y = 0, as in the event
log. The treasure may land on the landing square.

Implements: treasure-island/pirates-and-treasure, treasure-island/grid-and-crew, treasure-island/shared-squares, treasure-island/failed-move, treasure-island/failed-move-cost, treasure-island/actions, treasure-island/one-action-per-turn, treasure-island/turn-order
"""

import dataclasses
import random

_STEPS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}


@dataclasses.dataclass(frozen=True)
class Result:
    ok: bool
    message: str
    found_treasure: bool = False


class GameState:
    def __init__(self, grid_size, crew_size, landing_square, seed):
        rng = random.Random(seed)
        self.grid_size = grid_size
        self.treasure = (rng.randrange(grid_size), rng.randrange(grid_size))
        self.positions = [tuple(landing_square)] * crew_size
        self.treasure_dug_up = False
        self.turn = 0

    @property
    def current_pirate(self):
        return self.turn % len(self.positions)

    def _on_grid(self, x, y):
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def _end_turn(self, result):
        self.turn += 1
        return result

    def move(self, direction):
        """Move the current pirate one square. A move that can't happen costs the turn."""
        if direction not in _STEPS:
            known = ", ".join(_STEPS)
            message = f"There is no direction '{direction}': use one of {known}."
            return self._end_turn(Result(False, message))
        x, y = self.positions[self.current_pirate]
        step_x, step_y = _STEPS[direction]
        target = (x + step_x, y + step_y)
        if not self._on_grid(*target):
            message = f"You can't move {direction}: ({x}, {y}) is at the grid's edge."
            return self._end_turn(Result(False, message))
        self.positions[self.current_pirate] = target
        message = f"You moved {direction} to ({target[0]}, {target[1]})."
        return self._end_turn(Result(True, message))

    def dig(self):
        """Dig the current pirate's square. Once dug up, the treasure stays dug up."""
        if self.positions[self.current_pirate] != self.treasure:
            return self._end_turn(Result(True, "You dug here and found nothing."))
        self.treasure_dug_up = True
        return self._end_turn(
            Result(True, "You dug here and found the treasure!", True)
        )
