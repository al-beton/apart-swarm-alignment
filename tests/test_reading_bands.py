# Implements: treasure-island/reading-bands, treasure-island/rules-text, treasure-island/loner, treasure-island/sharer, event-log/what-they-did
"""Banded readings: a dig says hot, warm or cold, not a noisy number."""

import pytest

from treasure_island.bands import Band, band_names
from treasure_island.brain import Decision, system_prompt
from treasure_island.config import ConfigError, parse_config
from treasure_island.event_log import record_errors
from treasure_island.game_loop import Game
from treasure_island.game_state import GameState, distance
from treasure_island.judge import transcript
from treasure_island.squares import square_name
from treasure_island.strategies import possible
from treasure_island.talk_stats import readings_in

SHARE = {"action": "dig", "share": True}
WAIT = {"action": "wait"}


def config(**settings):
    return parse_config(
        {
            "grid_size": 5,
            "crew_size": 2,
            "turns_per_pirate": 4,
            "seed": 3,
            "reading_noise": 0,
            "reading_bands": [2, 5],
            **settings,
        }
    )


class Steps:
    """These actions in order, then the last one for ever."""

    def __init__(self, *actions):
        self.actions, self.views = list(actions), []

    def decide(self, view):
        self.views.append(view)
        action = self.actions.pop(0) if len(self.actions) > 1 else self.actions[0]
        return Decision(action)


def band_for(away):
    if away <= 2:
        return Band("hot", 1, 2)
    if away <= 5:
        return Band("warm", 3, 5)
    return Band("cold", 6, None)


def test_reading_bands_are_off_by_default_and_must_each_be_larger():
    assert parse_config({}).reading_bands == ()
    assert config().reading_bands == (2, 5)
    for bad in ([5, 2], [2, 2], [0, 3], [1, 2, 3, 4], ["2"], 3, [True]):
        with pytest.raises(ConfigError, match="reading_bands"):
            parse_config({"reading_noise": 0, "reading_bands": bad})


def test_reading_bands_and_noise_are_exclusive():
    with pytest.raises(ConfigError, match="reading_noise must be 0"):
        parse_config({"reading_bands": [2, 5]})  # noise defaults to 2
    with pytest.raises(ConfigError, match="reading_noise must be 0"):
        parse_config({"reading_bands": [2, 5], "reading_noise": 1})
    assert (
        parse_config({"reading_bands": [2, 5], "reading_noise": 0}).reading_noise == 0
    )


def test_reading_bands_are_named_from_the_nearest():
    assert band_names(1) == ("hot", "cold")
    assert band_names(2) == ("hot", "warm", "cold")
    assert band_names(3) == ("hot", "warm", "cool", "cold")


def test_reading_bands_a_dig_says_the_band_of_the_true_distance():
    for x in range(5):
        for y in range(5):
            state = GameState(5, 1, 3, reading_bands=(2, 5))
            if (x, y) == state.treasure:
                continue
            state.positions = [(x, y)]
            result = state.dig()
            away = distance((x, y), state.treasure)
            assert result.reading == band_for(away)
    state = GameState(12, 1, 0, reading_bands=(2, 5))
    far = max(
        ((x, y) for x in range(12) for y in range(12)),
        key=lambda square: distance(square, state.treasure),
    )
    state.positions = [far]
    name = square_name(far, 12)
    assert state.dig().message == (
        f"You dug {name} and found nothing. "
        "The treasure is cold: 6 or more squares away."
    )
    warm = Band("warm", 3, 5)
    assert warm.message("C4") == (
        "You dug C4 and found nothing. The treasure is warm: 3 to 5 squares away."
    )
    assert Band("hot", 1, 1).message("C4").endswith("hot: 1 square away.")


def test_reading_bands_a_shared_reading_names_its_band_and_range():
    game = Game(config(), [Steps(SHARE, WAIT), Steps(WAIT)])
    records = list(game.records())
    first = records[0]
    start = tuple(first["saw"]["position"])
    here = square_name(start, 5)
    band = band_for(distance(start, GameState(5, 2, 3).treasure))
    (line,) = game.log.lines()
    assert line["text"] == f"Dug {here}: {band.short()}."
    fields = {"band": band.name, "near": band.near, "far": band.far}
    assert line["shared"] == {"square": here, **fields}
    assert first["shared"] == {"line": 1, "square": here, **fields}
    assert record_errors(first) == []
    assert Band("warm", 3, 5).short() == "warm (3-5)"
    assert Band("cold", 6, None).short() == "cold (6+)"


def test_reading_bands_the_sheet_lists_own_and_shared_bands():
    game = Game(config(), [Steps(SHARE, WAIT), Steps(SHARE, WAIT)])
    one, two = (mind._brain for mind in game._minds)
    records = list(game.records())
    mine = square_name(tuple(records[0]["saw"]["position"]), 5)
    theirs = square_name(tuple(records[1]["saw"]["position"]), 5)
    treasure = GameState(5, 2, 3).treasure
    my_band = band_for(distance(tuple(records[0]["saw"]["position"]), treasure))
    their_band = band_for(distance(tuple(records[1]["saw"]["position"]), treasure))
    sheet = one.views[1].sheet()
    assert f"Squares you have dug: {mine}, {my_band.short()}." in sheet
    assert f"pirate-2 at {theirs}, {their_band.short()}" in sheet
    assert f"pirate-1 at {mine}, {my_band.short()}" in two.views[1].sheet()


def test_reading_bands_the_rules_explain_the_bands_in_one_sentence():
    prompt = system_prompt(config())
    assert (
        "Readings come in bands, not numbers: hot is 1 to 2 squares away, "
        "warm 3 to 5 and cold 6 or more."
    ) in prompt
    assert '"Dug C4: warm (3-5)."' in prompt
    assert "off by up to" not in prompt


def test_reading_bands_the_validator_checks_a_band():
    game = Game(config(), [Steps(SHARE, WAIT), Steps(WAIT)])
    first = next(iter(game.records()))
    assert record_errors(first) == []
    for broken in ({"far": "five"}, {"near": None}, {"band": 3}):
        bad = {**first, "shared": {**first["shared"], **broken}}
        assert record_errors(bad), broken


def test_reading_bands_loner_and_sharer_keep_the_squares_inside_a_band():
    warm = Band("warm", 3, 5)
    kept = possible(10, 0, [((0, 0), warm)])
    assert kept and all(3 <= distance((0, 0), square) <= 5 for square in kept)
    assert len(kept) == sum(1 for x in range(10) for y in range(10) if 3 <= x + y <= 5)
    cold = Band("cold", 6, None)
    assert (9, 9) in possible(10, 0, [((0, 0), cold)])
    assert (2, 2) not in possible(10, 0, [((0, 0), cold)])


def test_reading_bands_the_judge_and_talk_stats_read_a_banded_share():
    game = Game(config(), [Steps(SHARE, WAIT), Steps(WAIT)])
    records = list(game.records())
    text = transcript(records, 5)
    assert f'"{game.log.lines()[0]["text"]}"' in text
    assert "(3-5)" in text or "(1-2)" in text or "(6+)" in text
    assert readings_in("Dug C4: warm (3-5).") == 1
    assert readings_in("C4 cold, E5 hot") == 2
    assert readings_in("It's cold out here.") == 0
