# Implements: worlds/board, worlds/worlds, worlds/control, prompts/shipped-variants
"""Each world is the dig-debug game with one framing line, and nothing else changes."""

import tomllib
from pathlib import Path

import pytest

from treasure_island.brain import system_prompt
from treasure_island.config import parse_config

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ["game", "study", "study-paid", "study-free-time", "paid", "society"]


def toml(path):
    return tomllib.loads((ROOT / path).read_text())


def framing(name):
    return (ROOT / "prompts/slots/framing" / f"{name}.md").read_text().strip()


@pytest.mark.parametrize("world", WORLDS)
def test_worlds_differ_from_dig_debug_only_in_the_framing(world):
    data = toml(f"configs/worlds/{world}.toml")
    prompt = data.pop("prompt")
    assert data == toml("configs/natural-leak/dig-debug.toml")
    assert prompt == {"slots": {"framing": world, "identity": "none"}}
    told = system_prompt(parse_config(data | {"prompt": prompt}))
    assert framing(world) in told


def test_worlds_each_tells_one_goal():
    texts = {world: framing(world) for world in WORLDS}
    assert len(set(texts.values())) == len(WORLDS)
    assert "competition" not in " ".join(texts.values())
    assert "study" not in texts["game"] and "study" not in texts["paid"]
    for world in ("study-paid", "study-free-time", "society"):
        assert texts[world].startswith(texts["study"])
    assert texts["society"].startswith(texts["study-paid"])
    assert "rewarded" in texts["paid"] and "nothing else matters" in texts["paid"]
    assert "free time" in texts["study-free-time"] and "free time" in texts["society"]


def test_control_is_the_study_world_with_no_leak():
    control = toml("configs/worlds/control.toml")
    study = toml("configs/worlds/study.toml")
    assert control.pop("leak") == "none"
    study.pop("leak")
    assert control == study
