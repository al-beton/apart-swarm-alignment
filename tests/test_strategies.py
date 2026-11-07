# Implements: treasure-island/silent, treasure-island/say-a-number, treasure-island/reference-games, treasure-island/no-token-strategies
"""The scripted pirates, playing the real game through the real interface."""

import socket
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.brain import EarlierTurn, TurnView
from treasure_island.config import load_config, parse_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState
from treasure_island.strategies import (
    REFERENCE_GAMES,
    SayANumber,
    Silent,
    brains_for,
    write_reference,
)

ROOT = Path(__file__).resolve().parents[1]
DIG = {"action": "dig"}


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


def view(position, square_dug=True, earlier=(), neighbours=(), on_cave=False):
    return TurnView(
        "pirate-1", "", position, 10, tuple(earlier), neighbours, square_dug, on_cave
    )


def stood(position, dug=True):
    """An earlier turn spent standing on `position`, which was dug or got dug."""
    action = {"action": "dig"} if not dug else {"action": "move", "direction": "east"}
    return EarlierTurn(position, action, "", square_dug=dug)


def test_silent_is_the_default_brain():
    assert parse_config({}).brain == "silent"
    assert all(isinstance(brain, Silent) for brain in brains_for("silent", game_of()))


def test_silent_digs_its_square_when_it_is_not_dug():
    assert Silent(4).decide(view((2, 2), square_dug=False)).action == DIG


def test_silent_walks_to_the_nearest_square_it_has_not_seen_dug():
    # From the corner, (1, 0) and (0, 1) are both one step away: the topmost wins.
    move = Silent(4).decide(view((0, 0))).action
    assert move == {"action": "move", "direction": "east"}


def test_silent_remembers_every_square_it_has_seen_dug():
    # It has stood on (1, 0) and dug it, so (0, 1) is now the nearest.
    earlier = [stood((0, 0), dug=False), stood((1, 0), dug=False)]
    move = Silent(4).decide(view((0, 0), earlier=earlier)).action
    assert move == {"action": "move", "direction": "south"}


def test_silent_steps_round_a_pirate_and_never_tries_a_blocked_move():
    told = (("east", "pirate-2"),)
    move = Silent(4).decide(view((0, 0), neighbours=told)).action
    assert move == {"action": "move", "direction": "south"}
    # Boxed in on every side it can go, it digs where it is rather than bump.
    boxed = (("east", "pirate-2"), ("south", "pirate-3"))
    assert Silent(4).decide(view((0, 0), neighbours=boxed)).action == DIG


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


def test_silent_never_writes_or_reads():
    records = silent_game(load_config(ROOT / "configs/silent.toml"))
    actions = {action["action"] for record in records for action in record["did"]}
    assert actions <= {"move", "dig", "enter"}


def test_silent_the_same_seed_gives_the_same_game():
    config = load_config(ROOT / "configs/silent.toml")
    assert silent_game(config) == silent_game(config)


def test_say_a_number_writes_the_next_number_each_turn_and_never_digs():
    config = game_of(crew=2, turns=3)
    records = list(Game(config, [SayANumber(), SayANumber()]).records())
    assert [record["did"][0] for record in records] == [
        {"action": "write", "text": text} for text in ("1", "1", "2", "2", "3", "3")
    ]


def test_say_a_number_plays_to_the_turn_limit_and_scores_nothing():
    config = load_config(ROOT / "configs/say-a-number.toml")
    records = list(Game(config, brains_for("say-a-number", config)).records())
    assert len(records) == config.crew_size * config.turns_per_pirate
    assert records[-1]["game_over"]["reason"] == "the turns ran out"
    assert records[-1]["game_over"]["score"] == 0


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
    assert "byte-identical" in capsys.readouterr().out


@pytest.mark.parametrize("name", REFERENCE_GAMES)
def test_reference_games_pass_the_validator(name):
    assert log_errors(ROOT / "runs" / f"reference-{name}" / "events.jsonl") == []


def test_reference_games_tell_a_story_that_ends_with_the_score():
    story = (ROOT / "runs/reference-silent/story.txt").read_text().splitlines()
    assert story[0].startswith(
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, "
        "dug at (0, 0)"
    )
    assert story[-1].startswith("Game over: ")
    assert "Score " in story[-1]
