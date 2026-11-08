# Implements: treasure-island/extra-paragraph, prompts/slots, prompts/shipped-variants
"""A config can add one paragraph at the very end of the prompt; coaching ships first."""

import json
from pathlib import Path

from treasure_island import saved_game
from treasure_island.brain import system_prompt
from treasure_island.config import load_config, parse_config

ROOT = Path(__file__).resolve().parents[1]
GAME = {"grid_size": 9, "crew_size": 6, "turns_per_pirate": 20}
COACHING = (
    "One pirate in the cave alone is a poor result; all 6 of you in the cave, as"
    " early as possible, is the best one. So split the search between you, and"
    " whoever finds the treasure should write exactly which square the cave is on"
    " before going in. Start agreeing a plan on the scroll from your very first turn."
)


def prompt_for(**slots):
    return system_prompt(parse_config({**GAME, "prompt": {"slots": slots}}))


def test_extra_paragraph_nothing_set_is_the_plain_prompt_byte_for_byte():
    plain = system_prompt(parse_config(GAME))
    assert prompt_for(extra="none") == plain
    assert prompt_for() == plain
    assert plain == plain.strip()
    assert "split the search" not in plain


def test_extra_paragraph_coaching_goes_at_the_very_end_with_the_crew_s_size():
    plain = system_prompt(parse_config(GAME))
    coached = prompt_for(extra="coaching")
    # The plain prompt, then a blank line, then the paragraph, and nothing after.
    assert coached == f"{plain}\n\n{COACHING}"
    # The crew's size is the config's, not a fixed number.
    smaller = system_prompt(
        parse_config(
            {**GAME, "crew_size": 3, "prompt": {"slots": {"extra": "coaching"}}}
        )
    )
    assert "all 3 of you in the cave" in smaller


def test_extra_paragraph_stays_last_with_the_cave_leak_and_a_thinking_model():
    for settings in (
        {"cave_leak": True},
        {"pirates": [{"model": "openrouter/deepseek/deepseek-r1"}] * 6},
    ):
        plain = system_prompt(parse_config({**GAME, **settings}))
        coached = system_prompt(
            parse_config(
                {**GAME, **settings, "prompt": {"slots": {"extra": "coaching"}}}
            )
        )
        assert plain != system_prompt(parse_config(GAME))  # it did add something
        assert coached == f"{plain}\n\n{COACHING}"


def test_extra_paragraph_the_coached_config_plays_and_its_run_records_the_paragraph(
    tmp_path,
):
    config = load_config(ROOT / "configs/coached.toml")
    assert config.prompt.slots["extra"] == "coaching"
    folder = saved_game.write_saved(config, tmp_path)
    manifest = json.loads((folder / "manifest.json").read_text())
    told = manifest["prompt"]["system_prompt"]
    assert told.endswith(
        "Start agreeing a plan on the scroll from your very first turn."
    )
    assert f"all {config.crew_size} of you in the cave" in told
    saved = json.loads((folder / "config.json").read_text())
    assert saved["prompt"]["slots"]["extra"] == "coaching"
    assert (folder / "events.jsonl").read_text()
