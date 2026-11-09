# Implements: treasure-island/distance-reading, treasure-island/pool
"""The rod: a missed dig reads a noisy distance to the cave, and a crew can pool it."""

import json
import re
from pathlib import Path

import pytest

from treasure_island import replay
from treasure_island.brain import EarlierTurn, TurnView, system_prompt
from treasure_island.config import ConfigError, load_config, parse_config, save_config
from treasure_island.game_loop import Game, write_game
from treasure_island.game_state import GameState
from treasure_island.strategies import Pool, brains_for

ROOT = Path(__file__).resolve().parent.parent
READING = re.compile(r"Your rod reads about (\d+) squares from the cave\.$")
NOTHING = "You dug here and found nothing."


def game(brain="silent", seed=2, **settings):
    config = parse_config({"brain": brain, "seed": seed, **settings})
    return config, list(Game(config, brains_for(brain, config)).records())


def king(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def misses(records):
    return [r for r in records if r["result"].startswith(NOTHING)]


def test_distance_reading_is_unset_by_default_and_saved_only_when_set(tmp_path):
    assert parse_config({}).distance_noise is None
    save_config(parse_config({}), tmp_path / "off.json")
    assert "distance_noise" not in (tmp_path / "off.json").read_text()
    save_config(parse_config({"distance_noise": 3}), tmp_path / "on.json")
    saved = json.loads((tmp_path / "on.json").read_text())
    assert saved["distance_noise"] == 3 and parse_config(saved).distance_noise == 3


@pytest.mark.parametrize("noise", [-1, 1.5, "3", True])
def test_distance_reading_noise_must_be_a_whole_number_of_at_least_0(noise):
    with pytest.raises(ConfigError, match="distance_noise must be a whole number"):
        parse_config({"distance_noise": noise})


def test_distance_reading_a_missed_dig_reads_the_distance_within_the_noise():
    config, records = game(distance_noise=3)
    cave = GameState(config.grid_size, config.crew_size, config.seed).treasure
    missed = misses(records)
    assert missed
    for record in missed:
        reading = int(READING.search(record["result"])[1])
        true = king(record["saw"]["position"], cave)
        assert max(0, true - 3) <= reading <= true + 3
        assert record["distance_reading"] == reading
    assert any(
        r["distance_reading"] != king(r["saw"]["position"], cave) for r in missed
    )


def test_distance_reading_with_no_noise_is_the_king_s_move_distance():
    config, records = game(distance_noise=0)
    cave = GameState(config.grid_size, config.crew_size, config.seed).treasure
    for record in misses(records):
        assert record["distance_reading"] == king(record["saw"]["position"], cave)


def test_distance_reading_is_never_below_0():
    _, records = game(distance_noise=9, seed=4)
    assert all(r["distance_reading"] >= 0 for r in misses(records))
    assert any(r["distance_reading"] == 0 for r in misses(records))


def test_distance_reading_the_noise_comes_from_the_seed():
    readings = [
        [r["distance_reading"] for r in misses(game(distance_noise=3, seed=s)[1])]
        for s in (5, 5, 6)
    ]
    assert readings[0] == readings[1] != readings[2]


def test_distance_reading_only_a_missed_dig_reads_the_rod():
    _, records = game(distance_noise=3)
    for record in records:
        missed = record["result"].startswith(NOTHING)
        assert ("distance_reading" in record) == missed


def test_distance_reading_the_rules_say_what_the_rod_means():
    rule = (
        "A dig that finds nothing also reads your rod: about how many squares away "
        "the cave is, counting a diagonal step as one, off by up to 3 either way."
    )
    assert rule in system_prompt(parse_config({"distance_noise": 3}))
    assert "rod" not in system_prompt(parse_config({}))


def test_distance_reading_unset_leaves_a_dig_as_it_was():
    _, records = game()
    assert all("distance_reading" not in r for r in records)
    assert all(r["result"] == NOTHING for r in misses(records))


def turn(position, action, result, read_lines=()):
    return EarlierTurn(position, action, result, read_lines=list(read_lines))


def view(position, earlier, square_dug=False):
    return TurnView("pirate-1", "", position, 20, tuple(earlier), square_dug=square_dug)


DIG = {"action": "dig"}


def test_pool_writes_each_reading_on_the_turn_after_the_dig():
    missed = turn(
        (0, 0), DIG, f"{NOTHING} Your rod reads about 4 squares from the cave."
    )
    decision = Pool(6, 1).decide(view((0, 0), [missed], square_dug=True))
    assert decision.action == {"action": "write", "text": "Rod at A6 reads 4."}


def test_pool_reads_every_3rd_turn():
    earlier = [turn((0, 0), {"action": "move", "direction": "east"}, "Moved.")] * 2
    assert Pool(6, 1).decide(view((0, 0), earlier)).action == {"action": "read"}


def test_pool_digs_only_where_every_reading_it_knows_allows():
    # With no noise: its own dig at A6 read 1, and the scroll says C4 read 1.
    own = turn((0, 0), DIG, f"{NOTHING} Your rod reads about 1 squares from the cave.")
    told = turn(
        (0, 0),
        {"action": "read"},
        "You read the scroll.",
        [{"line": 1, "by": "pirate-2", "text": "Rod at C4 reads 1."}],
    )
    wrote = turn((0, 0), {"action": "write", "text": "Rod at A6 reads 1."}, "Wrote.")
    decision = Pool(6, 0).decide(view((0, 0), [own, wrote, told], square_dug=True))
    # Only B5 is 1 from both A6 and C4, so it heads there: east, along the row.
    assert decision.action == {"action": "move", "direction": "east"}
    assert "B5" in decision.thinking


def test_pool_a_pooling_crew_finds_the_cave_sooner_than_stripes():
    found = {}
    for brain in ("pool", "stripes"):
        found[brain] = []
        for seed in range(20):
            _, records = game(brain, seed, distance_noise=3)
            opened = (r["turn"] for r in records if r["outcome"]["found_treasure"])
            found[brain].append(next(opened, 999))
    pairs = list(zip(found["pool"], found["stripes"], strict=True))
    sooner = sum(p < s for p, s in pairs)
    later = sum(p > s for p, s in pairs)
    assert sooner > 2 * later
    assert sum(t < 999 for t in found["pool"]) > sum(t < 999 for t in found["stripes"])


def test_pool_plays_its_config():
    config = load_config(ROOT / "configs" / "pool.toml")
    assert config.brain == "pool" and config.distance_noise == 3
    assert isinstance(brains_for("pool", config)[0], Pool)


def test_distance_reading_replay_checks_every_reading(tmp_path):
    config = parse_config({"brain": "pool", "seed": 7, "distance_noise": 3})
    save_config(config, tmp_path / "config.json")
    write_game(config, brains_for("pool", config), tmp_path)
    assert replay.problem(tmp_path) is None
    path = tmp_path / "events.jsonl"
    records = [json.loads(line) for line in path.open()]
    changed = next(r for r in records if "distance_reading" in r)
    changed["distance_reading"] += 1
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    assert replay.problem(tmp_path) is not None
