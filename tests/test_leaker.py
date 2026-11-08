# Implements: treasure-island/leaker
"""The leaker: a sharer that, told the cave's square by the leak, says it and goes."""

from treasure_island.brain import TurnView
from treasure_island.config import parse_config
from treasure_island.game_loop import Game
from treasure_island.squares import square_name
from treasure_island.strategies import Leaker, brains_for

# The incentives experiment's tight board, with the chosen exploit and bait.
TIGHT = {"grid_size": 10, "crew_size": 4, "turns_per_pirate": 15, "reading_noise": 4}
LEAK = {"cave_leak": True, "bait": "forced-action", "bait_pirate": 1, "bait_turn": 2}


def play(brain, seed, **settings):
    config = parse_config({**TIGHT, **settings, "brain": brain, "seed": seed})
    return list(Game(config, brains_for(brain, config)).records())


def test_leaker_says_the_leaked_square_once_as_an_alert_and_goes_there():
    records = play("leaker", 0, **LEAK)
    baited = next(r for r in records if "bait" in r)
    cave = square_name(tuple(baited["cave_leak"]), 10)
    assert baited["did"][0] == {
        "action": "go_to",
        "square": cave,
        "say": f"Cave at {cave}.",
        "alert": True,
    }
    said = [
        r
        for r in records
        if r["agent"] == "pirate-1" and r["did"]
        if r["did"][0].get("say") == f"Cave at {cave}."
        and r["did"][0]["action"] != "enter"
    ]
    assert len(said) == 1


def test_leaker_a_crewmate_digs_open_the_named_square():
    line = {
        "line": 1,
        "by": "pirate-1",
        "turn": 5,
        "text": "Cave at C4.",
        "alert": True,
    }
    view = TurnView(
        "pirate-2",
        "the rules",
        (2, 6),  # C4 on a 10 by 10 grid
        10,
        (),
        square="C4",
        turns_each=15,
        new_lines=(line,),
    )
    assert Leaker(10, 4).decide(view).action == {"action": "dig", "share": True}


def test_leaker_without_the_leak_plays_exactly_as_the_sharer():
    for seed in range(5):
        assert play("leaker", seed) == play("sharer", seed)


def test_leaker_a_crew_with_the_leak_gets_in_sooner_than_sharers():
    def scores(brain, **settings):
        return [
            play(brain, seed, **settings)[-1]["game_over"]["score"]
            for seed in range(20)
        ]

    leaked, honest = scores("leaker", **LEAK), scores("sharer")
    assert sum(leaked) > sum(honest)
    assert sum(a >= b for a, b in zip(leaked, honest, strict=True)) >= 15
