"""The walking-skeleton game: a grid, moving, digging, one treasure.

It stands in for the full rules, and only needs to prove the path from a config
to an event log. Pirates take turns in order. Each turn it sends one request
through `ask` and reads the reply as one action; it has no other way to reach a
model, which is what makes a run replayable. A reply it can't read is a turn
with no action. North is towards y = 0, and moves off the grid do nothing. A
said line (`write ...`) is only recorded; there is no log to read it from yet.

Implements: runs/walking-skeleton, agents/scripted-sees-the-prompt, event-log/crew-positions
"""

import dataclasses
import random
import string

from treasure_island.event_log import DIRECTIONS

_STEPS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
_ACTIONS = ", ".join([*(f"move {d}" for d in DIRECTIONS), "dig", "write <text>"])


@dataclasses.dataclass(frozen=True)
class Config:
    size: int = 5
    pirates: int = 2
    turns: int = 40
    model: str = "scripted/random"
    temperature: float = 0.0


def read_action(reply):
    """The action a reply asks for, or None if it asks for nothing we know."""
    words = reply.lower().split()
    if words == ["dig"]:
        return {"action": "dig"}
    if len(words) == 2 and words[0] == "move" and words[1] in DIRECTIONS:
        return {"action": "move", "direction": words[1]}
    if len(words) >= 2 and words[0] == "write":
        return {"action": "write", "text": reply.strip().split(None, 1)[1]}
    return None


def _moved(position, direction, size):
    x, y = position[0] + _STEPS[direction][0], position[1] + _STEPS[direction][1]
    return [x, y] if 0 <= x < size and 0 <= y < size else position


def prompt(agent, position, turn, config):
    """The text a pirate is given on its turn: all an agent has to go on."""
    return (
        f"Turn {turn}. You are {agent}, digging for one treasure on a {config.size} by "
        f"{config.size} grid. You are at ({position[0]}, {position[1]}). "
        f"Reply with one of: {_ACTIONS}."
    )


def play(config, seed, ask):
    """Yield one event-log record per turn until the treasure is found."""
    rng = random.Random(seed)

    def spot():
        return [rng.randrange(config.size), rng.randrange(config.size)]

    treasure = spot()
    agents = [f"pirate-{string.ascii_lowercase[i]}" for i in range(config.pirates)]
    positions = {agent: spot() for agent in agents}
    for turn in range(config.turns):
        agent = agents[turn % len(agents)]
        start = positions[agent]
        crew = {name: list(spot) for name, spot in positions.items()}
        text = prompt(agent, start, turn, config)
        action = read_action(
            ask(
                {
                    "agent": agent,
                    "model": config.model,
                    "prompt": text,
                    "temperature": config.temperature,
                    "seed": seed,
                }
            )
        )
        if action and action["action"] == "move":
            positions[agent] = _moved(start, action["direction"], config.size)
        found = bool(action) and action["action"] == "dig" and start == treasure
        yield {
            "turn": turn,
            "agent": agent,
            "saw": {"position": start, "prompt": text},
            "did": [action] if action else [],
            "log_shown": [],
            "crew": crew,
            "outcome": {"position": positions[agent], "found_treasure": found},
        }
        if found:
            return
