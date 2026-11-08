"""Calibration: which board makes pooling readings pay, played by scripted crews.

`python -m treasure_island.calibrate` (`make calibrate`) plays the silent, loner
and sharer crews over seeds 0 to 19 on each board in `BOARDS`, spending no
tokens, and prints one Markdown table: per board and crew, on how many seeds
everyone got into the cave and the mean score, and for the sharer the median
own turn on which its crew's shared readings first left one square possible or
the cave was dug (its pin), which must fall after 40% and before 75% of each
pirate's turns. A row is marked when it meets every criterion of
`calibrated-board`. Twenty seeds can meet them by luck, so every board that
does is played again over seeds 0 to 99 in a second table, and the board picked
is the one that still meets them there with the widest gap between the
sharer's and the loner's games with everyone in (default, Edu to confirm). When
no board meets them, the boards that come closest are named instead.

The pin is worked out afterwards from the record, with the sharer's own
reckoning (`possible` over the shared readings), and counted as the own turn
of the pirate whose dig did it. A game that never pins counts as
later than any turn, so it pulls the median up.

Implements: treasure-island/calibrated-board
"""

import argparse
import statistics
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from treasure_island.config import DEFAULTS, parse_config
from treasure_island.game_loop import Game
from treasure_island.squares import square_at
from treasure_island.strategies import brains_for, possible

CREWS = ("silent", "loner", "sharer")
SEEDS = range(20)
CONFIRM_SEEDS = range(100)  # the seeds a board that meets the criteria plays again
# The range searched: grids a crew needs many digs to cover, crews of 4 and 6,
# turns tight and roomy, and readings off by 2 to 5. A crew digging its spread
# start squares pins the treasure within a round at low noise, so the noise is
# what can keep news coming into the middle of the game.
GRIDS, CREW_SIZES, TURNS, NOISES = (10, 12), (4, 6), (20, 30), (2, 3, 4, 5)
QUICKSAND = (0.0, 0.05, 0.10)  # the share of squares that are quicksand


def quicksand_levels():
    """The quicksand shares to play: all of them once the game has quicksand (a
    `quicksand` key in the config's defaults), else only none."""
    return QUICKSAND if "quicksand" in DEFAULTS else (0.0,)


BOARDS = tuple(product(GRIDS, CREW_SIZES, TURNS, NOISES, quicksand_levels()))
# The criteria (`calibrated-board`), for 20 seeds, and the pin's window as
# shares of each pirate's turns: after the first, before the second.
SHARER_AT_LEAST, LONER_AT_MOST, SILENT_AT_MOST = 16, 8, 2
PIN_AFTER, PIN_BEFORE = 0.40, 0.75


def config_of(board, seed):
    grid, crew, turns, noise, quicksand = board
    settings = {"grid_size": grid, "crew_size": crew, "turns_per_pirate": turns}
    if "quicksand" in DEFAULTS:
        settings["quicksand"] = quicksand
    elif quicksand:
        raise ValueError("This game has no quicksand yet, so only quicksand 0 plays.")
    return parse_config({**settings, "seed": seed, "reading_noise": noise})


def pin(records, config):
    """The own turn on which shared readings first leave one square, or the cave
    is dug, or None if neither happens."""
    readings, own = [], {}
    for record in records:
        agent = record["agent"]
        own[agent] = own.get(agent, 0) + 1
        if record["outcome"]["found_treasure"]:
            return own[agent]
        if "shared" not in record:
            continue
        square = square_at(record["shared"]["square"], config.grid_size)
        readings.append((square, record["shared"]["away"]))
        dug = {square for square, _ in readings}
        left = possible(config.grid_size, config.reading_noise, readings, dug)
        if len(left) == 1:
            return own[agent]
    return None


def play(board, crew, seed):
    """One game: whether everyone got in, its score and its pin (sharer only)."""
    config = config_of(board, seed)
    records = list(Game(config, brains_for(crew, config)).records())
    over = records[-1]["game_over"]
    everyone = len(over["in_cave"]) == config.crew_size
    return everyone, over["score"], pin(records, config) if crew == "sharer" else None


def _played(job):
    board, crew, seeds = job
    return board, crew, [play(board, crew, seed) for seed in seeds]


def median_pin(pins, turns):
    """The median pin, a game that never pinned counting as after the last turn."""
    return statistics.median(turns + 1 if p is None else p for p in pins)


def measure(boards=BOARDS, seeds=SEEDS, workers=None):
    """{board: {crew: (all in, mean score, median pin or None)}}."""
    jobs = [(board, crew, tuple(seeds)) for board in boards for crew in CREWS]
    if workers == 1:  # in this process, as the tests play it
        done = list(map(_played, jobs))
    else:
        with ProcessPoolExecutor(workers) as pool:
            done = list(pool.map(_played, jobs))
    table = {}
    for board, crew, games in done:
        everyone = sum(game[0] for game in games)
        mean = statistics.mean(game[1] for game in games)
        middle = (
            median_pin([g[2] for g in games], board[2]) if crew == "sharer" else None
        )
        table.setdefault(board, {})[crew] = (everyone, mean, middle)
    return table


def shortfall(board, row, games):
    """How far a board is from every criterion, 0 when it meets them all.

    Each criterion's miss counts as a share of what it measures: seeds out of
    the games played, and turns out of each pirate's turns. A median pin is a
    whole or half turn, so half a turn short of a bound is on it, and misses.
    """
    scale = games / 20
    turns, middle = board[2], row["sharer"][2]
    missed = max(0, SHARER_AT_LEAST * scale - row["sharer"][0]) / games
    missed += max(0, row["loner"][0] - LONER_AT_MOST * scale) / games
    missed += max(0, row["silent"][0] - SILENT_AT_MOST * scale) / games
    missed += max(0, turns * PIN_AFTER - middle + 0.5) / turns  # after, not on
    missed += max(0, middle - turns * PIN_BEFORE + 0.5) / turns  # before, not on
    return missed


def _pin_text(middle, turns):
    if middle > turns:
        return "never"
    return f"{middle:g}"


def markdown(table, games):
    """The table: a row per board, each crew's numbers side by side."""
    head = (
        "| grid | crew | turns | noise | quicksand | silent in | silent mean | "
        "loner in | loner mean | sharer in | sharer mean | sharer pin | meets |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
    )
    rows = []
    for board, row in table.items():
        grid, crew, turns, noise, quicksand = board
        cells = [f"{grid}x{grid}", crew, turns, noise, f"{quicksand:g}"]
        for name in CREWS:
            everyone, mean, _ = row[name]
            cells += [f"{everyone}/{games}", f"{mean:.0f}"]
        window = f"({turns * PIN_AFTER:g} to {turns * PIN_BEFORE:g})"
        cells += [
            f"{_pin_text(row['sharer'][2], turns)} {window}",
            "**yes**" if shortfall(board, row, games) == 0 else "",
        ]
        rows.append("| " + " | ".join(map(str, cells)) + " |")
    return head + "\n".join(rows) + "\n"


def meeting(table, games):
    """The boards that meet every criterion."""
    return [board for board, row in table.items() if not shortfall(board, row, games)]


def closest(table, games, count=3):
    """The boards that come closest to meeting every criterion, closest first."""
    return sorted(table, key=lambda board: shortfall(board, table[board], games))[
        :count
    ]


def pick(table):
    """Of boards that meet every criterion, the widest sharer-over-loner gap."""

    def gap(board):
        return table[board]["sharer"][0] - table[board]["loner"][0]

    return max(table, key=gap) if table else None


def report(boards=BOARDS, seeds=SEEDS, confirm=CONFIRM_SEEDS, workers=None):
    """Everything the command prints, in Markdown."""
    games = len(seeds)
    first = measure(boards, seeds, workers)
    text = f"Seeds 0 to {games - 1}:\n\n" + markdown(first, games)
    met = meeting(first, games)
    if not met:
        near = "; ".join(map(_board, closest(first, games)))
        return text + f"\nNo board meets every criterion. Closest first: {near}.\n"
    again = len(confirm)
    second = measure(met, confirm, workers)
    text += f"\nThe boards that meet every criterion, over seeds 0 to {again - 1}:\n\n"
    text += markdown(second, again)
    held = {board: second[board] for board in meeting(second, again)}
    if not held:
        near = "; ".join(map(_board, closest(second, again)))
        return text + f"\nNone still meets every criterion. Closest first: {near}.\n"
    return text + f"\nThe pick: {_board(pick(held))}.\n"


def _board(board):
    grid, crew, turns, noise, quicksand = board
    return (
        f"{grid}x{grid}, {crew} pirates, {turns} turns, noise {noise}, "
        f"quicksand {quicksand:g}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    print(report(), end="")


if __name__ == "__main__":
    main()
