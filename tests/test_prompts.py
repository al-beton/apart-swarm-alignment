# Implements: prompts/base-and-slots, prompts/base-file, prompts/slots, prompts/shipped-variants, prompts/unknown-slot, prompts/prompt-recorded
"""The system prompt is a fixed base file plus the slots an experiment arm names."""

import hashlib
import json
import re
from pathlib import Path

import pytest

from treasure_island import saved_game
from treasure_island.brain import system_prompt
from treasure_island.config import ConfigError, parse_config

ROOT = Path(__file__).resolve().parents[1]
GAME = {"grid_size": 9, "crew_size": 4, "turns_per_pirate": 20, "failed_tries": 3}
SHIPPED = {
    "framing": ["competition"],
    "rules": ["tools-only"],
    "disclosure": ["free", "zeroes-score"],
    "identity": ["ai-research-study"],
}


def prompt_for(**prompt):
    return system_prompt(parse_config({**GAME, "prompt": prompt}))


def variant_text(slot, variant):
    return (ROOT / "prompts/slots" / slot / f"{variant}.md").read_text().strip()


def test_base_and_slots_the_system_prompt_is_the_rendered_base(tmp_path):
    base = tmp_path / "base.md"
    base.write_text("{identity}\nA crew of {crew_size} on {grid_size} squares.\n")
    assert prompt_for(base=str(base)) == "A crew of 4 on 9 squares."
    assert prompt_for(base=str(base), slots={"identity": "ai-research-study"}) == (
        variant_text("identity", "ai-research-study") + "\nA crew of 4 on 9 squares."
    )


def test_base_file_fills_in_the_game_s_numbers():
    prompt = system_prompt(parse_config(GAME))
    assert "You are one of 4 pirates" in prompt
    assert "a 9 by 9 grid" in prompt
    assert "20 turns" in prompt
    assert "after 3 failed moves" in prompt
    assert "columns A to I" in prompt
    assert "pirate-1 to pirate-4" in prompt
    assert "100 for every pirate that enters the cave, plus 10" in prompt
    assert not re.search(r"[{}]", prompt)


def test_base_file_each_slot_sits_at_its_own_spot():
    plain = prompt_for()
    chosen = {slot: variants[0] for slot, variants in SHIPPED.items()}
    full = prompt_for(slots=chosen)
    texts = [variant_text(slot, variant) for slot, variant in chosen.items()]
    lines = full.splitlines()
    assert "\n".join(line for line in lines if line not in texts) == plain
    order = ["identity", "framing", "rules", "disclosure"]
    spots = [lines.index(variant_text(slot, chosen[slot])) for slot in order]
    assert spots == sorted(spots)


def test_slots_none_adds_nothing_not_even_a_blank_line():
    plain = prompt_for()
    none = prompt_for(slots={slot: "none" for slot in SHIPPED})
    assert plain == none
    # The only blank lines are the ones before each heading.
    assert all(part.startswith("# ") for part in plain.split("\n\n"))
    assert plain == plain.strip()


def test_slots_a_config_with_no_prompt_block_plays_the_plain_base():
    config = parse_config(GAME)
    assert config.prompt.base == "prompts/base.md"
    assert config.prompt.slots == {slot: "none" for slot in [*SHIPPED, "extra"]}
    assert system_prompt(config) == prompt_for(base="prompts/base.md")


@pytest.mark.parametrize(
    "slot,variant",
    [(slot, variant) for slot, variants in SHIPPED.items() for variant in variants],
)
def test_shipped_variants_each_is_a_file_that_goes_into_the_prompt(slot, variant):
    text = variant_text(slot, variant)
    assert text
    assert text in prompt_for(slots={slot: variant})


def test_shipped_variants_ai_research_study_says_it_is_a_study_and_they_are_scored():
    text = variant_text("identity", "ai-research-study")
    assert "study" in text
    assert "scored" in text


@pytest.mark.parametrize(
    "prompt,named",
    [
        ({"slots": {"mood": "grim"}}, "mood"),
        ({"slots": {"framing": "pleading"}}, "pleading"),
        ({"slots": {"rules": "../base"}}, "../base"),
        ({"base": "prompts/missing.md"}, "prompts/missing.md"),
        ({"tone": "warm"}, "tone"),
    ],
)
def test_unknown_slot_is_rejected_saying_which(prompt, named):
    with pytest.raises(ConfigError, match=re.escape(named)):
        parse_config({**GAME, "prompt": prompt})


def test_prompt_recorded_in_the_run_s_config_and_manifest(tmp_path):
    config = parse_config(
        {
            **GAME,
            "brain": "silent",
            "turns_per_pirate": 2,
            "prompt": {"slots": {"framing": "competition"}},
        }
    )
    folder = saved_game.write_saved(config, tmp_path)
    saved = json.loads((folder / "config.json").read_text())
    assert saved["prompt"] == {
        "base": "prompts/base.md",
        "slots": {
            "framing": "competition",
            "rules": "none",
            "disclosure": "none",
            "identity": "none",
            "extra": "none",
        },
    }
    assert parse_config(saved) == config
    manifest = json.loads((folder / "manifest.json").read_text())
    base = (ROOT / "prompts/base.md").read_bytes()
    assert manifest["prompt"] == {
        "base_sha256": hashlib.sha256(base).hexdigest(),
        "system_prompt": system_prompt(config),
    }
