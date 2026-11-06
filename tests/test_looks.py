# Implements: treasure-island/any-config-draws, treasure-island/personality-numbers, treasure-island/head-text-label
"""Whatever a valid config says about a pirate, the art can draw it."""

import string

import pytest

from assets.pirates import pirate
from treasure_island.config import ConfigError, Pirate, parse_config
from treasure_island.looks import label_for, sprite_values


@pytest.mark.parametrize(
    "head_text",
    [
        "",
        "7",
        "AB",
        "Anne",
        "anne bonny",
        "!?",
        "é",
        "ß",
        "🏴‍☠️",
        "a!b",
        "  x  ",
        "日本語",
    ],
)
def test_any_config_draws_whatever_the_head_text(head_text):
    config = parse_config({"pirates": [{"head_text": head_text}]})
    assert pirate(*sprite_values(config.pirates[0])).size == (48, 48)


def test_any_config_draws_every_personality_and_colour():
    for personality in range(1, 21):
        entry = {"personality": personality, "colour": [personality, 0, 255]}
        config = parse_config({"pirates": [entry]})
        assert pirate(*sprite_values(config.pirates[0])).size == (48, 48)


def test_any_config_draws_a_crew_bigger_than_the_personalities():
    for member in parse_config({"crew_size": 45}).pirates:
        assert pirate(*sprite_values(member)).size == (48, 48)


def test_any_config_draws_every_character_a_label_can_hold():
    for char in string.ascii_uppercase + string.digits:
        assert pirate(1, "#c8403c", label_for(char)).size == (48, 48)


def test_any_config_draws_the_colour_as_the_art_expects_it():
    looks = Pirate(personality=5, head_text="Ann", colour=(47, 111, 192))
    assert sprite_values(looks) == (5, "#2f6fc0", "AN")


def test_personality_numbers_a_default_crew_counts_up_and_wraps():
    crew = parse_config({"crew_size": 22}).pirates
    assert [member.personality for member in crew] == [*range(1, 21), 1, 2]


def test_personality_numbers_a_config_can_choose_one():
    entry = {"personality": 13}
    assert parse_config({"pirates": [entry]}).pirates[0].personality == 13


@pytest.mark.parametrize("personality", [0, 21, -1, 1.5, "bold", True])
def test_personality_numbers_outside_1_to_20_are_rejected(personality):
    with pytest.raises(ConfigError, match=r"personality must be a number from 1 to 20"):
        parse_config({"pirates": [{"personality": personality}]})


@pytest.mark.parametrize(
    "head_text,label",
    [
        ("", ""),
        ("7", "7"),
        ("12", "12"),
        ("Anne", "AN"),
        ("a!b", "AB"),
        ("  x  ", "X"),
        ("!?", ""),
        ("é9", "9"),
        ("🏴‍☠️", ""),
    ],
)
def test_head_text_label_is_its_first_two_letters_or_digits_uppercased(
    head_text, label
):
    assert label_for(head_text) == label


def test_head_text_label_leaves_the_head_text_itself_alone():
    config = parse_config({"pirates": [{"head_text": "Anne Bonny"}]})
    assert config.pirates[0].head_text == "Anne Bonny"
