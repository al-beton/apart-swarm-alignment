"""A game's config: every lever as a variable, with the spec's defaults.

A TOML file sets any of the fields below. `pirates` is an optional list of
tables, one per pirate; leave a key out, or the whole list, to get its default.
`parse_config` reports every problem at once, so one fix-and-retry is enough.

Implements: treasure-island/config-variables, treasure-island/grid-and-crew, treasure-island/scarce-turns, treasure-island/crew-varies, treasure-island/pirate-definition, treasure-island/personality-numbers, treasure-island/graphics-elsewhere, treasure-island/brain-in-config
"""

import colorsys
import dataclasses
import json
import tomllib
from pathlib import Path

DEFAULTS = {
    "grid_size": 10,
    "crew_size": 6,
    "turns_per_pirate": 30,
    "landing_square": (0, 0),
    "log_window": 3,
    "read_size": 3,
    "seed": 0,
    "brain": "s-sweep",
}
# The smallest value each whole-number field may take. A log window of 0 turns
# the free window off. Seeds can be any whole number.
_MINIMUMS = {
    "grid_size": 1,
    "crew_size": 1,
    "turns_per_pirate": 1,
    "log_window": 0,
    "read_size": 1,
}
PERSONALITIES = 20  # the art draws this many, numbered from 1


class ConfigError(ValueError):
    """A config that can't be played. The message names every problem."""


@dataclasses.dataclass(frozen=True)
class Pirate:
    personality: int
    head_text: str
    colour: tuple[int, int, int]


@dataclasses.dataclass(frozen=True)
class GameConfig:
    grid_size: int
    crew_size: int
    turns_per_pirate: int
    landing_square: tuple[int, int]
    log_window: int
    read_size: int
    seed: int
    brain: str
    pirates: tuple[Pirate, ...]


def _is_int(value):
    # bool is a subclass of int, but `true` is not a size.
    return isinstance(value, int) and not isinstance(value, bool)


def _is_colour(value):
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(_is_int(part) and 0 <= part <= 255 for part in value)
    )


def _default_colour(index, crew_size):
    # Hues spaced evenly round the wheel, so any crew can be told apart.
    rgb = colorsys.hsv_to_rgb(index / crew_size, 0.8, 0.9)
    return tuple(round(part * 255) for part in rgb)


def _pirate_errors(where, entry):
    if not isinstance(entry, dict):
        return [f"{where} must be a table"]
    errors = [
        f"{where}.{key} is not a pirate setting"
        for key in entry
        if key not in ("personality", "head_text", "colour")
    ]
    personality = entry.get("personality", 1)
    if not _is_int(personality) or not 1 <= personality <= PERSONALITIES:
        errors.append(f"{where}.personality must be a number from 1 to {PERSONALITIES}")
    if not isinstance(entry.get("head_text", ""), str):
        errors.append(f"{where}.head_text must be text")
    if "colour" in entry and not _is_colour(entry["colour"]):
        errors.append(f"{where}.colour must be [red, green, blue], each 0 to 255")
    return errors


def _crew_errors(data):
    if "pirates" not in data:
        return []
    pirates = data["pirates"]
    if not isinstance(pirates, list) or not pirates:
        return ["pirates must be a list of at least one pirate"]
    errors = [
        error
        for index, entry in enumerate(pirates)
        for error in _pirate_errors(f"pirates[{index}]", entry)
    ]
    if "crew_size" in data and data["crew_size"] != len(pirates):
        errors.append(
            f"crew_size is {data['crew_size']} but pirates lists {len(pirates)}"
        )
    return errors


def _number_errors(data):
    errors = []
    for key, minimum in _MINIMUMS.items():
        value = data.get(key, DEFAULTS[key])
        if not _is_int(value) or value < minimum:
            errors.append(f"{key} must be a whole number of at least {minimum}")
    if not _is_int(data.get("seed", DEFAULTS["seed"])):
        errors.append("seed must be a whole number")
    if not isinstance(data.get("brain", DEFAULTS["brain"]), str):
        errors.append("brain must be the name of a brain")
    return errors


def _landing_errors(data):
    if "landing_square" not in data:
        return []
    square = data["landing_square"]
    size = data.get("grid_size", DEFAULTS["grid_size"])
    if (
        not isinstance(square, list)
        or len(square) != 2
        or not all(_is_int(part) for part in square)
    ):
        return ["landing_square must be [x, y]"]
    if _is_int(size) and not all(0 <= part < size for part in square):
        return [f"landing_square {square} is off a grid of size {size}"]
    return []


def _problems(data):
    unknown = [
        f"{key} is not a config setting"
        for key in data
        if key not in DEFAULTS and key != "pirates"
    ]
    return [
        *unknown,
        *_number_errors(data),
        *_landing_errors(data),
        *_crew_errors(data),
    ]


def _pirate(index, crew_size, entry):
    colour = entry.get("colour")
    return Pirate(
        personality=entry.get("personality", index % PERSONALITIES + 1),
        head_text=entry.get("head_text", str(index + 1)),
        colour=tuple(colour) if colour else _default_colour(index, crew_size),
    )


def parse_config(data):
    """A checked GameConfig from plain values, or a ConfigError naming each problem."""
    problems = _problems(data)
    if problems:
        raise ConfigError("; ".join(problems))
    settings = {**DEFAULTS, **{k: v for k, v in data.items() if k != "pirates"}}
    entries = data.get("pirates", [{}] * settings["crew_size"])
    crew_size = len(entries)
    settings["crew_size"] = crew_size
    settings["landing_square"] = tuple(settings["landing_square"])
    pirates = tuple(
        _pirate(index, crew_size, entry) for index, entry in enumerate(entries)
    )
    return GameConfig(pirates=pirates, **settings)


def load_config(path):
    """A checked GameConfig from a TOML file."""
    try:
        data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"{Path(path).name} is not valid TOML: {error}") from error
    return parse_config(data)


def save_config(config, path):
    """Write every lever, defaults included, so `parse_config` can read it back."""
    text = json.dumps(dataclasses.asdict(config), indent=2, sort_keys=True)
    Path(path).write_text(text + "\n", encoding="utf-8")
