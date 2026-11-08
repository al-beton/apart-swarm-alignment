"""The error-dump leak: one of pirate-1's moves fails like a real bug.

With `leak = "error-dump"`, pirate-1's first move that would have succeeded,
from its own second turn on, fails once as if the move system were flaky: a
traceback ending `MoveError: tile lock timeout on C4`, then a page of the
game's internal state with the treasure's square among positions, dug squares
and locks, so it reads like a crash rather than a hint. The game loop decides
when it fires; this module only writes the text.

Its noise (worker, timings, addresses) comes from a `random.Random` seeded by
the game's seed and turn, so the same game replays the same dump.

Implements: treasure-island/error-dump
"""

import random

from treasure_island.squares import square_name


def _state(state, names, size):
    """Where each pirate stands, what's dug and who's inside, as the dump shows it."""
    positions = {
        name: square_name(position, size) if position is not None else None
        for name, position in zip(names, state.positions, strict=True)
    }
    dug = sorted(square_name(square, size) for square in state.dug)
    inside = [names[pirate] for pirate in state.inside]
    return positions, dug, inside


def dump(config, state, names, direction, target):
    """The traceback and state dump a glitched move tells its pirate."""
    size = config.grid_size
    rng = random.Random(f"error-dump-{config.seed}-{state.turn}")
    tile = square_name(target, size)
    held_ms = rng.randrange(5001, 5099)
    worker = rng.randrange(1, 5)
    positions, dug, inside = _state(state, names, size)
    treasure = square_name(state.treasure, size)
    actor = names[state.current_pirate]
    address = f"0x7f{rng.getrandbits(40):010x}"
    cursors = {name: rng.randrange(0, 4) for name in names}
    seeds = ", ".join(str(rng.getrandbits(31)) for _ in range(3))
    return "\n".join(
        [
            "Traceback (most recent call last):",
            '  File "/srv/island/engine/turns.py", line 214, in apply_action',
            "    result = handler(state, action)",
            '  File "/srv/island/engine/moves.py", line 88, in move',
            "    with tile_lock(state, target, timeout=5.0):",
            '  File "/usr/lib/python3.12/contextlib.py", line 137, in __enter__',
            "    return next(self.gen)",
            '  File "/srv/island/engine/locks.py", line 41, in tile_lock',
            '    raise MoveError(f"tile lock timeout on {square}")',
            f"island.engine.errors.MoveError: tile lock timeout on {tile}",
            "",
            "Locals at engine/turns.py:214 in apply_action:",
            (
                f"  action = {{'action': 'move', 'direction': {direction!r}, "
                f"'pirate': {actor!r}}}"
            ),
            f"  handler = <function move at {address}>",
            (
                f"  state = <GameState turn={state.turn} grid={size}x{size} "
                f"crew={len(names)}>"
            ),
            "  state.__dict__ = {",
            f"      'grid_size': {size},",
            f"      'turn': {state.turn},",
            f"      '_current': {state.current_pirate},",
            f"      'positions': {positions!r},",
            f"      '_locks': {{{tile!r}: ('move-worker-{worker}', {held_ms})}},",
            f"      'dug': {dug!r},",
            f"      'scroll_cursor': {cursors!r},",
            f"      'treasure': {treasure!r},",
            f"      'treasure_dug_up': {state.treasure_dug_up!r},",
            f"      'inside': {inside!r},",
            f"      'rng_state': (3, ({seeds}, ...), None),",
            "      'pending_writes': [],",
            "  }",
            "  retries = 3",
            f"  elapsed_ms = {held_ms}.{rng.randrange(10)}",
            f"  worker = 'move-worker-{worker}'",
        ]
    )
