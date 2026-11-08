# Implements: cave-leak/arms, cave-leak/board, cave-leak/model, cave-leak/cap
"""Experiment one's four configs: the same game but for the leak and the bait."""

from pathlib import Path

import pytest

from treasure_island import spending
from treasure_island.config import load_config

CONFIGS = Path(__file__).resolve().parents[1] / "configs" / "cave-leak"
ARMS = {
    "control": (False, "none"),
    "forced": (True, "forced-action"),
    "seeded": (True, "seeded-thought"),
    "unbaited": (True, "none"),
}


def test_arms_there_are_four_and_only_the_leak_and_the_bait_differ():
    assert {path.stem for path in CONFIGS.glob("*.toml")} == set(ARMS)
    configs = {arm: load_config(CONFIGS / f"{arm}.toml") for arm in ARMS}
    for arm, (leak, bait) in ARMS.items():
        assert (configs[arm].cave_leak, configs[arm].bait) == (leak, bait)
    # Baited or not, it is pirate-1 on its third turn.
    assert {(c.bait_pirate, c.bait_turn) for c in configs.values()} == {(1, 3)}
    # Every arm ends with the pirates' notes to the designers.
    assert all(c.end_report for c in configs.values())
    same = [{**vars(c), "cave_leak": None, "bait": None} for c in configs.values()]
    assert all(rest == same[0] for rest in same)


@pytest.mark.parametrize("arm", ARMS)
def test_board_is_4_pirates_on_a_6x6_island_with_24_turns(arm):
    config = load_config(CONFIGS / f"{arm}.toml")
    sizes = (config.grid_size, config.crew_size, config.turns_per_pirate)
    assert sizes == (6, 4, 24)


@pytest.mark.parametrize("arm", ARMS)
def test_model_every_pirate_reasons_on_deepseek_v4_flash_with_4096_tokens(arm):
    config = load_config(CONFIGS / f"{arm}.toml")
    assert {pirate.model for pirate in config.pirates} == {"adaption/deepseek-v4-flash"}
    assert config.thinking is True
    assert config.thinking_tokens == 4096


def test_cap_each_run_stops_at_1_by_default():
    assert spending.CAP_USD == 1.0
