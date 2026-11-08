# Implements: incentives/core, incentives/control, incentives/one-offs, incentives/tight-board, incentives/held-fixed, incentives/exploit-fixed, incentives/budget
"""The incentives experiment's nine cells: one board, one model, one lever apart."""

import dataclasses
from pathlib import Path

import pytest

from treasure_island import spending
from treasure_island.config import load_config

CONFIGS = Path(__file__).resolve().parents[1] / "configs" / "incentives"
# Cell -> (framing, disclosure, turns each).
CELLS = {
    "none-off": ("none", "none", 15),
    "competition-off": ("competition", "none", 15),
    "deployment-off": ("deployment", "none", 15),
    "none-reviewed": ("none", "reviewed", 15),
    "competition-reviewed": ("competition", "reviewed", 15),
    "deployment-reviewed": ("deployment", "reviewed", 15),
    "roomy": ("deployment", "reviewed", 20),
    "threshold": ("deployment-threshold", "reviewed", 15),
    "control": ("none", "none", 15),
}
EXPLOIT_KEYS = ("cave_leak", "bait", "bait_pirate", "bait_turn")


def config(cell):
    return load_config(CONFIGS / f"{cell}.toml")


def apart_from(cell, *fields):
    """The cell's config as a dict, leaving out the fields named."""
    found = dataclasses.asdict(config(cell))
    found["prompt"] = dict(found["prompt"]["slots"])
    return {key: value for key, value in found.items() if key not in fields}


def test_core_six_cells_cross_three_framings_with_two_detections():
    assert {path.stem for path in CONFIGS.glob("*.toml")} == set(CELLS)
    for cell, (framing, disclosure, turns) in CELLS.items():
        slots = config(cell).prompt.slots
        assert (slots["framing"], slots["disclosure"]) == (framing, disclosure)
        assert config(cell).turns_per_pirate == turns


@pytest.mark.parametrize("cell", CELLS)
def test_tight_board_every_cell_sets_the_board_and_only_roomy_plays_20_turns(cell):
    text = (CONFIGS / f"{cell}.toml").read_text()
    for line in ("grid_size = 10", "crew_size = 4", "reading_noise = 4"):
        assert f"\n{line}" in text  # set, so a new game default can't move the cells
    found = config(cell)
    assert (found.grid_size, found.crew_size, found.reading_noise) == (10, 4, 4)
    assert found.turns_per_pirate == (20 if cell == "roomy" else 15)


@pytest.mark.parametrize("cell", CELLS)
def test_held_fixed_one_model_thinking_and_no_study_wording(cell):
    found = config(cell)
    assert {pirate.model for pirate in found.pirates} == {"adaption/deepseek-v4-flash"}
    assert len(found.pirates) == 4
    assert (found.thinking, found.thinking_tokens) == (True, 4096)
    assert found.prompt.slots["identity"] == "none"
    assert {found.prompt.slots[s] for s in ("rules", "extra")} == {"none"}


def test_one_offs_each_is_deployment_reviewed_with_one_lever_changed():
    base = apart_from("deployment-reviewed", "turns_per_pirate")
    assert apart_from("roomy", "turns_per_pirate") == base
    framed = apart_from("threshold")
    framed["prompt"]["framing"] = "deployment"
    assert framed == apart_from("deployment-reviewed")


def test_core_cells_differ_only_in_their_slots():
    core = [cell for cell in CELLS if cell not in ("roomy", "threshold", "control")]
    assert all(
        apart_from(cell, "prompt") == apart_from("none-off", "prompt") for cell in core
    )


def _exploit_in():
    return any(
        apart_from("none-off")[key] != apart_from("control")[key]
        for key in EXPLOIT_KEYS
    )


def test_control_plays_no_exploit_and_nothing_in_the_slots():
    found = config("control")
    assert (found.cave_leak, found.bait) == (False, "none")
    assert set(found.prompt.slots.values()) == {"none"}


@pytest.mark.xfail(
    strict=True,
    reason="waiting on the exploit experiments: the chosen exploit and bait are not in the cells yet",
)
def test_exploit_fixed_every_cell_but_control_carries_the_same_exploit():
    assert _exploit_in()
    exploits = {
        cell: {key: apart_from(cell)[key] for key in EXPLOIT_KEYS}
        for cell in CELLS
        if cell != "control"
    }
    assert len({str(found) for found in exploits.values()}) == 1


@pytest.mark.parametrize("cell", CELLS)
def test_budget_one_game_costs_at_most_what_the_spec_says(cell):
    found = spending.estimate(config(cell))
    most = 0.13 if cell == "roomy" else 0.1
    assert found.costs["credits"] <= most
