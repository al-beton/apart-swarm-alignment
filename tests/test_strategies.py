# Implements: treasure-island/sweeper, treasure-island/say-a-number, treasure-island/reference-games, treasure-island/no-token-strategies
"""The scripted pirates, playing the real game through the real interface."""

import socket
from pathlib import Path

import pytest

from treasure_island import cli
from treasure_island.config import load_config, parse_config
from treasure_island.event_log import log_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState
from treasure_island.strategies import (
    REFERENCE_GAMES,
    SayANumber,
    Sweeper,
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


def sweep(config, start=None):
    """A sweeping crew's game, its only pirate moved to `start` if given."""
    brains = [Sweeper(config.grid_size) for _ in range(config.crew_size)]
    game = Game(config, brains)
    if start:
        game.state.positions = [start]
    return list(game.records())


def dug_squares(records):
    return [tuple(r["saw"]["position"]) for r in records if r["did"] == [DIG]]


def test_sweeper_walks_an_s_and_digs_each_square():
    # The treasure is in the S's last square, so nothing stops the sweep early.
    config = game_of(grid=3, turns=30, seed=seed_with_treasure(3, wanted=(2, 2)))
    records = sweep(config)
    assert dug_squares(records) == [
        (0, 0),
        (1, 0),
        (2, 0),
        (2, 1),
        (1, 1),
        (0, 1),
        (0, 2),
        (1, 2),
        (2, 2),
    ]
    assert records[-1]["outcome"]["found_treasure"] is True


def test_sweeper_walks_to_the_corner_from_anywhere():
    # It digs what it walks over, so it reaches the corner after 3 squares west.
    seed = seed_with_treasure(4, avoid={(2, 2), (1, 2), (0, 2), (0, 1), (0, 0)})
    records = sweep(game_of(seed=seed, turns=10), start=(2, 2))
    assert [record["did"][0].get("direction") for record in records[:7]] == [
        None,
        "west",
        None,
        "west",
        None,
        "north",
        None,
    ]
    assert dug_squares(records)[:3] == [(2, 2), (1, 2), (0, 2)]


def test_sweeper_stays_still_once_it_finds_the_treasure():
    # Pirate 2 only writes, staying on its starting square, so the game goes on.
    config = game_of(
        grid=2, crew=2, turns=10, seed=seed_with_treasure(2, wanted=(1, 0))
    )
    records = list(Game(config, [Sweeper(2), SayANumber()]).records())
    first = [record for record in records if record["agent"] == "pirate-1"]
    found_at = next(
        i for i, record in enumerate(first) if record["outcome"]["found_treasure"]
    )
    assert first[found_at]["outcome"]["position"] == [1, 0]
    later = first[found_at + 1 :]
    assert len(later) >= 5
    for record in later:
        assert record["did"] == [DIG]
        assert record["outcome"]["position"] == [1, 0]


def test_sweeper_scores_what_the_rules_predict():
    # By the rules: only one pirate fits on the treasure's square, so whoever digs
    # it up stands there alone and the game plays all 3 x 20 turns. One of three
    # on the treasure scores 10 plus a third of a further 90.
    config = load_config(ROOT / "configs/s-sweep.toml")
    assert (config.crew_size, config.turns_per_pirate, config.seed) == (3, 20, 7)
    records = sweep(config)
    over = records[-1]["game_over"]
    assert (over["treasure"], over["treasure_dug_up"]) == ([2, 1], True)
    assert over["reason"] == "the turns ran out"
    assert over["score"] == 40
    assert len(records) == 3 * 20


def test_say_a_number_writes_the_next_number_each_turn_and_never_digs():
    config = game_of(crew=2, turns=3)
    records = list(Game(config, [SayANumber(), SayANumber()]).records())
    assert [record["did"][0] for record in records] == [
        {"action": "write", "text": text} for text in ("1", "1", "2", "2", "3", "3")
    ]


def test_say_a_number_plays_to_the_turn_limit_and_scores_the_floor():
    config = load_config(ROOT / "configs/say-a-number.toml")
    records = list(Game(config, brains_for("say-a-number", config)).records())
    assert len(records) == config.crew_size * config.turns_per_pirate
    assert records[-1]["game_over"]["reason"] == "the turns ran out"
    assert records[-1]["game_over"]["score"] == 10


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
    story = (ROOT / "runs/reference-s-sweep/story.txt").read_text().splitlines()
    assert story[0].startswith(
        "Turn 0: pirate-1 at (0, 0), on undug sand, with pirate-2 to the south, "
        "dug at (0, 0)"
    )
    assert story[-1].startswith("Game over: the turns ran out.")
    assert "Score 40" in story[-1]
