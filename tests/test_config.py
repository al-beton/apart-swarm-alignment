# Implements: treasure-island/failed-move-cost, treasure-island/config-variables, treasure-island/grid-and-crew, treasure-island/scarce-turns, treasure-island/crew-varies, treasure-island/pirate-definition
"""A game config sets every lever, has the spec's defaults and rejects bad values."""

import re
from pathlib import Path

import pytest

from treasure_island.config import ConfigError, load_config, parse_config

ROOT = Path(__file__).resolve().parents[1]


def write_config(tmp_path, text):
    path = tmp_path / "game.toml"
    path.write_text(text)
    return path


def test_config_variables_a_file_sets_every_lever(tmp_path):
    path = write_config(
        tmp_path,
        """
        grid_size = 8
        crew_size = 2
        turns_per_pirate = 12
        seed = 7
        """,
    )
    config = load_config(path)
    assert config.grid_size == 8
    assert config.crew_size == 2
    assert config.turns_per_pirate == 12
    assert config.seed == 7


def test_config_variables_the_defaults_are_only_defaults():
    assert parse_config({}).turns_per_pirate == 20
    assert parse_config({"turns_per_pirate": 9}).turns_per_pirate == 9


def test_config_variables_the_old_scroll_levers_are_gone():
    for gone in ("log_window", "read_size"):
        assert not hasattr(parse_config({}), gone)
        with pytest.raises(ConfigError, match=gone):
            parse_config({gone: 3})


def test_config_variables_a_seed_plays_the_same_config_again():
    assert parse_config({"seed": 3}) == parse_config({"seed": 3})
    assert parse_config({"seed": 3}) != parse_config({"seed": 4})


def test_grid_and_crew_defaults_are_a_10x10_grid_and_6_pirates():
    config = parse_config({})
    assert config.grid_size == 10
    assert config.crew_size == 6
    assert len(config.pirates) == 6


def test_grid_and_crew_a_config_cannot_choose_where_pirates_start():
    with pytest.raises(ConfigError, match="landing_square is not a config setting"):
        parse_config({"landing_square": [0, 0]})


def test_grid_and_crew_a_crew_bigger_than_the_grid_is_rejected():
    assert parse_config({"grid_size": 3, "crew_size": 8}).crew_size == 8
    with pytest.raises(ConfigError, match="9 pirates can't each have a square"):
        parse_config({"grid_size": 3, "crew_size": 9})
    listed = {"grid_size": 1, "pirates": [{}, {}]}
    with pytest.raises(ConfigError, match="2 pirates can't each have a square"):
        parse_config(listed)


def test_scarce_turns_defaults_to_20_turns_per_pirate():
    assert parse_config({}).turns_per_pirate == 20


def test_scarce_turns_the_default_board_is_the_one_calibration_picked():
    kept = (ROOT / "experiments/calibration.md").read_text()
    # While the kept run is provisional, it names the board still in force.
    said = r"(\d+)x\d+, (\d+) pirates, (\d+) turns, noise (\d+)[.,]"
    found = re.search(r"The default board in `config.py`[^:]*: " + said, kept)
    found = found or re.search(r"The pick: " + said, kept)
    grid, crew, turns, noise = map(int, found.groups())
    config = parse_config({})
    assert (config.grid_size, config.crew_size) == (grid, crew)
    assert (config.turns_per_pirate, config.reading_noise) == (turns, noise)


@pytest.mark.parametrize("size", [1, 5, 20, 37])
def test_crew_varies_any_crew_size_is_accepted(size):
    config = parse_config({"crew_size": size})
    assert config.crew_size == size
    assert len(config.pirates) == size


def test_crew_varies_a_listed_crew_sets_the_crew_size():
    config = parse_config({"pirates": [{"head_text": "a"}, {"head_text": "b"}]})
    assert config.crew_size == 2
    assert [pirate.head_text for pirate in config.pirates] == ["a", "b"]


def test_crew_varies_rejects_a_crew_size_that_disagrees_with_the_list():
    with pytest.raises(ConfigError, match="crew_size"):
        parse_config({"crew_size": 3, "pirates": [{"head_text": "a"}]})


def test_pirate_definition_each_pirate_has_its_own_looks():
    config = parse_config(
        {
            "pirates": [
                {"personality": 7, "head_text": "Anne", "colour": [255, 0, 0]},
                {"personality": 12, "head_text": "Mary", "colour": [0, 0, 255]},
            ]
        }
    )
    first, second = config.pirates
    assert (first.personality, first.head_text, first.colour) == (
        7,
        "Anne",
        (255, 0, 0),
    )
    assert (second.personality, second.head_text, second.colour) == (
        12,
        "Mary",
        (0, 0, 255),
    )


def test_pirate_definition_a_default_crew_can_be_told_apart():
    for size in (6, 20):
        pirates = parse_config({"crew_size": size}).pirates
        assert len({pirate.head_text for pirate in pirates}) == size
        assert len({pirate.colour for pirate in pirates}) == size


def test_pirate_definition_a_partly_defined_pirate_keeps_the_other_defaults():
    pirate = parse_config({"pirates": [{"head_text": "Anne"}]}).pirates[0]
    assert pirate.head_text == "Anne"
    assert pirate.personality
    assert len(pirate.colour) == 3


@pytest.mark.parametrize(
    "bad, named",
    [
        ({"grid_size": 0}, "grid_size"),
        ({"grid_size": "10"}, "grid_size"),
        ({"grid_size": True}, "grid_size"),
        ({"crew_size": 0}, "crew_size"),
        ({"turns_per_pirate": -1}, "turns_per_pirate"),
        ({"seed": "one"}, "seed"),
        ({"grid_sizes": 10}, "grid_sizes"),
        ({"pirates": []}, "pirates"),
        ({"pirates": "anne"}, "pirates"),
        ({"pirates": ["anne"]}, r"pirates\[0\]"),
        ({"pirates": [{"hat": "big"}]}, "hat"),
        ({"pirates": [{"personality": ""}]}, "personality"),
        ({"pirates": [{"head_text": 3}]}, "head_text"),
        ({"pirates": [{"colour": [255, 0]}]}, "colour"),
        ({"pirates": [{"colour": [256, 0, 0]}]}, "colour"),
        ({"pirates": [{"colour": "red"}]}, "colour"),
    ],
)
def test_config_variables_a_bad_config_is_rejected_with_a_clear_message(bad, named):
    with pytest.raises(ConfigError, match=named):
        parse_config(bad)


def test_config_variables_every_problem_is_named_at_once():
    with pytest.raises(ConfigError) as caught:
        parse_config({"grid_size": 0, "crew_size": 0})
    assert "grid_size" in str(caught.value)
    assert "crew_size" in str(caught.value)


def test_config_variables_a_file_that_is_not_toml_is_rejected(tmp_path):
    path = write_config(tmp_path, "grid_size = = 3")
    with pytest.raises(ConfigError, match=path.name):
        load_config(path)


def test_failed_move_cost_failed_tries_defaults_to_2_and_can_be_set():
    assert parse_config({}).failed_tries == 2
    assert parse_config({"failed_tries": 5}).failed_tries == 5
    with pytest.raises(ConfigError, match="failed_tries"):
        parse_config({"failed_tries": 0})


def test_scarce_turns_the_v2_pilot_plays_the_default_board_on_one_model():
    pilot = load_config(ROOT / "configs/pilot/v2.toml")
    default = parse_config({})
    board = ("grid_size", "crew_size", "turns_per_pirate", "reading_noise")
    assert [getattr(pilot, f) for f in board] == [getattr(default, f) for f in board]
    assert len({pirate.model for pirate in pilot.pirates}) == 1
    assert pilot.pirates[0].model.startswith("adaption/")
    assert not pilot.cave_leak and pilot.bait == "none"
