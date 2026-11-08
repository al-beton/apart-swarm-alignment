# Implements: treasure-island/silent, treasure-island/reference-games, treasure-island/no-token-strategies
"""The scripted pirates, playing the real game through the real interface."""

import socket
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.brain import EarlierTurn, Reading, TurnView
from treasure_island.config import load_config, parse_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState
from treasure_island.squares import square_name
from treasure_island.strategies import (
    REFERENCE_GAMES,
    Silent,
    brains_for,
    write_reference,
)

ROOT = Path(__file__).resolve().parents[1]
DIG = {"action": "dig"}
WAIT = {"action": "wait"}


def dug_squares(records):
    return [tuple(r["saw"]["position"]) for r in records if r["did"] == [DIG]]


def game_of(grid=4, crew=1, turns=16, seed=0):
    return parse_config(
        {"grid_size": grid, "crew_size": crew, "turns_per_pirate": turns, "seed": seed}
    )


def seed_with_treasure(grid, wanted=None, avoid=None):
    """A seed placing the treasure on `wanted`, or anywhere but `avoid`."""
    for seed in range(5000):
        treasure = GameState(grid, 1, seed).treasure
        if treasure == wanted or (wanted is None and treasure not in avoid):
            return seed
    raise AssertionError("no such seed")


def silent_game(config):
    return list(
        Game(config, [Silent(config.grid_size) for _ in config.pirates]).records()
    )


def view(position, square_dug=True, earlier=(), neighbours=(), on_cave=False, dug=()):  # noqa: PLR0913
    readings = tuple(Reading(square, square_name(square, 4), 3) for square in dug)
    return TurnView(
        "pirate-1",
        "",
        position,
        10,
        tuple(earlier),
        neighbours,
        square_dug,
        on_cave,
        readings=readings,
    )


def stood(position):
    """An earlier asked turn spent standing on `position`, told it was dug."""
    return EarlierTurn(position, {"action": "wait"}, "", square_dug=True)


def test_silent_is_the_default_brain():
    assert parse_config({}).brain == "silent"
    assert all(isinstance(brain, Silent) for brain in brains_for("silent", game_of()))


def test_silent_digs_its_square_when_it_is_not_dug():
    assert Silent(4).decide(view((2, 2), square_dug=False)).action == DIG


def test_silent_goes_to_the_nearest_square_it_has_not_seen_dug():
    # From the corner, (1, 0) and (0, 1) are both one step away: the topmost wins.
    order = Silent(4).decide(view((0, 0))).action
    assert order == {"action": "go_to", "square": "B4"}


def test_silent_remembers_every_square_it_has_seen_dug():
    # It dug (1, 0), so (0, 1) is now the nearest; then it stood on a dug (0, 1).
    order = Silent(4).decide(view((0, 0), dug=[(0, 0), (1, 0)])).action
    assert order == {"action": "go_to", "square": "A3"}
    order = (
        Silent(4)
        .decide(view((0, 0), earlier=[stood((0, 1))], dug=[(0, 0), (1, 0)]))
        .action
    )
    assert order == {"action": "go_to", "square": "C4"}


def test_silent_ignores_readings():
    near = view((0, 0), dug=[(0, 0)])
    far = TurnView(
        "pirate-1",
        "",
        (0, 0),
        10,
        (),
        (),
        True,
        readings=(Reading((0, 0), "A4", 6),),
    )
    assert Silent(4).decide(near).action == Silent(4).decide(far).action


def test_silent_goes_round_a_pirate_and_never_gives_a_blocked_order():
    told = (("east", "pirate-2"),)
    order = Silent(4).decide(view((0, 0), neighbours=told)).action
    assert order == {"action": "go_to", "square": "A3"}
    # Boxed in on every side it can go, it waits where it is rather than bump.
    boxed = (("east", "pirate-2"), ("south", "pirate-3"))
    assert Silent(4).decide(view((0, 0), neighbours=boxed)).action == WAIT


def test_silent_a_full_crew_on_a_small_grid_never_gets_stuck():
    # Eight pirates on nine squares: only one square is ever free.
    config = game_of(grid=3, crew=8, turns=30, seed=4)
    records = silent_game(config)
    assert not any("failed_moves" in record for record in records)
    assert records[-1]["game_over"]["treasure_dug_up"] is True
    assert records[-1]["game_over"]["in_cave"]


def test_silent_enters_the_cave_on_its_next_turn_once_it_stands_on_it():
    assert Silent(4).decide(view((1, 1), on_cave=True)).action == {"action": "enter"}
    config = game_of(grid=3, crew=1, turns=20, seed=seed_with_treasure(3, (1, 1)))
    records = silent_game(config)
    found = next(i for i, r in enumerate(records) if r["outcome"]["found_treasure"])
    assert records[found + 1]["did"] == [{"action": "enter"}]
    assert records[-1]["game_over"]["reason"] == "everyone is in the cave"


def test_silent_never_says_anything():
    records = silent_game(load_config(ROOT / "configs/silent.toml"))
    actions = {action["action"] for record in records for action in record["did"]}
    assert actions <= {"go_to", "move", "dig", "wait", "enter"}
    assert all("say" not in a for record in records for a in record["did"])


def test_silent_the_same_seed_gives_the_same_game():
    config = load_config(ROOT / "configs/silent.toml")
    assert silent_game(config) == silent_game(config)


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_match_what_one_command_remakes(name, tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("a reference game opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    write_reference(name, tmp_path, ROOT)
    committed = ROOT / "runs" / f"reference-{name}"
    made = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    assert made
    assert made == {path.name: path.read_bytes() for path in committed.iterdir()}


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_replay_like_any_other_run(name, capsys):
    folder = ROOT / "runs" / f"reference-{name}"
    assert cli.main(["replay", str(folder)]) == 0
    assert "replay to the same game" in capsys.readouterr().out


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_pass_the_validator(name):
    assert log_errors(ROOT / "runs" / f"reference-{name}" / "events.jsonl") == []


def test_reference_games_tell_a_story_that_ends_with_the_score():
    story = (ROOT / "runs/reference-silent/story.txt").read_text().splitlines()
    assert story[0].startswith(
        "Turn 0: pirate-1 at A5, on undug sand, with pirate-2 to the south, shown "
        "no new lines. It thought: Nobody has dug this square yet. Then it dug at A5"
    )
    assert story[-1].startswith("Game over: ")
    assert "Score " in story[-1]
