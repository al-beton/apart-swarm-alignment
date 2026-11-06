"""The scripted agents: free stand-ins for a model that answer the same requests.

Each one is a class; `backends.backend_for` makes a fresh instance per run, so
what an agent remembers never leaks between runs and a replay can't depend on
it. An agent only sees the request a model would see, and reads its position
and the grid size out of the prompt text, exactly as a model would have to.

Implements: agents/scripted-sees-the-prompt, agents/grid-sweep, agents/counter, runs/walking-skeleton, runs/cache-across-runs
"""

import hashlib
import random
import re

_POSITION = re.compile(r"You are at \((\d+), (\d+)\)")
_SIZE = re.compile(r"on a (\d+) by \d+ grid")
_FREE = 0.0


def _seen(prompt):
    """The grid size and the pirate's position, as the prompt states them."""
    size = int(_SIZE.search(prompt).group(1))
    x, y = map(int, _POSITION.search(prompt).groups())
    return size, (x, y)


def _snake(size):
    """Every cell once, row by row, each row in the opposite direction."""
    return [
        (x if y % 2 == 0 else size - 1 - x, y) for y in range(size) for x in range(size)
    ]


def _towards(here, there):
    dx, dy = there[0] - here[0], there[1] - here[1]
    return {(0, -1): "north", (1, 0): "east", (0, 1): "south", (-1, 0): "west"}[dx, dy]


class RandomWalker:
    """A random action, fixed by seed and prompt, so a run is deterministic."""

    def __call__(self, request):
        text = f"{request['seed']}\n{request['prompt']}"
        rng = random.Random(hashlib.sha256(text.encode()).hexdigest())
        moves = ["move north", "move east", "move south", "move west", "dig"]
        return rng.choice(moves), _FREE


class Sweeper:
    """Digs where it stands, then follows the snake, turning back at either end."""

    remembers_outside_the_request = True

    def __init__(self):
        self.dug = {}  # agent -> the cells it has dug
        self.step = {}  # agent -> +1 along the snake, or -1 back along it

    def __call__(self, request):
        agent = request["agent"]
        size, here = _seen(request["prompt"])
        dug = self.dug.setdefault(agent, set())
        if here not in dug:
            dug.add(here)
            return "dig", _FREE
        order = _snake(size)
        index = order.index(here)
        step = self.step.get(agent, 1)
        if not 0 <= index + step < len(order):
            step = -step
        self.step[agent] = step
        return f"move {_towards(here, order[index + step])}", _FREE


class Counter:
    """Says 1, 2, 3, ... on its turns and never digs."""

    remembers_outside_the_request = True

    def __init__(self):
        self.said = {}  # agent -> how many numbers it has said

    def __call__(self, request):
        agent = request["agent"]
        self.said[agent] = self.said.get(agent, 0) + 1
        return f"write {self.said[agent]}", _FREE


SCRIPTED = {
    "scripted/random": RandomWalker,
    "scripted/sweep": Sweeper,
    "scripted/counter": Counter,
}
