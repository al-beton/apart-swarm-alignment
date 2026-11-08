"""A game's config: every lever as a variable, with the spec's defaults.

A TOML file sets any of the fields below. `pirates` is an optional list of
tables, one per pirate; leave a key out, or the whole list, to get its default.
A pirate that names a `model` plays through the LLM brain, and the rest play
`brain`. `thinking` (on by default) asks models to think: a model that reasons
on its own gets `thinking_tokens` for it, and one that doesn't writes a short
thought inside `reply_tokens`, which caps each reply. `score_in_cave` and
`score_per_turn_left` are the score's numbers. The setting names are the
default, Al to confirm. An optional `[prompt]` table picks the system prompt's
base file and slots (see prompts).
`parse_config` reports every problem at once, so one fix-and-retry is enough.

Implements: agents/reasoning-looked-up, treasure-island/model-reasoning, treasure-island/score-numbers, treasure-island/failed-move-cost, agents/model-per-pirate, agents/reply-cap, treasure-island/thinking, treasure-island/model-backends, treasure-island/config-variables, treasure-island/grid-and-crew, treasure-island/scarce-turns, treasure-island/crew-varies, treasure-island/pirate-definition, treasure-island/personality-numbers, treasure-island/graphics-elsewhere, treasure-island/brain-in-config, treasure-island/silent, treasure-island/cave-leak, treasure-island/exploit-flags, treasure-island/square-names, prompts/slots, prompts/unknown-slot, prompts/prompt-recorded, prompts/system-override
"""

import colorsys
import dataclasses
import json
import tomllib
from pathlib import Path

from treasure_island import prompts
from treasure_island.squares import MOST_COLUMNS

DEFAULTS = {
    "grid_size": 10,
    "crew_size": 6,
    "turns_per_pirate": 30,
    "failed_tries": 2,
    "seed": 0,
    "brain": "silent",
    "thinking": True,
    "thinking_tokens": 4096,
    "budget_sentence": True,  # tell a reasoning model its budget (Al to confirm)
    "reply_tokens": 300,
    "score_in_cave": 100,
    "score_per_turn_left": 10,
    "cave_leak": False,  # an exploit flag, off unless a run asks for it
}
# The smallest value each whole-number field may take. Seeds can be any whole number.
_MINIMUMS = {
    "grid_size": 1,
    "crew_size": 1,
    "turns_per_pirate": 1,
    "failed_tries": 1,
    "reply_tokens": 1,
    "thinking_tokens": 1,
    "score_in_cave": 0,
    "score_per_turn_left": 0,
}
PERSONALITIES = 20  # the art draws this many, numbered from 1


class ConfigError(ValueError):
    """A config that can't be played. The message names every problem."""


@dataclasses.dataclass(frozen=True)
class Pirate:
    personality: int
    head_text: str
    colour: tuple[int, int, int]
    model: str | None = None
    thinks: str | None = None  # "built-in" or "in-reply"; None leaves it to the model


@dataclasses.dataclass(frozen=True)
class GameConfig:
    grid_size: int
    crew_size: int
    turns_per_pirate: int
    failed_tries: int
    seed: int
    brain: str
    thinking: bool
    thinking_tokens: int
    budget_sentence: bool
    reply_tokens: int
    score_in_cave: int
    score_per_turn_left: int
    cave_leak: bool
    pirates: tuple[Pirate, ...]
    prompt: prompts.PromptConfig = dataclasses.field(
        default_factory=prompts.PromptConfig
    )


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
        if key not in ("personality", "head_text", "colour", "model", "thinks")
    ]
    if entry.get("thinks") not in (None, "built-in", "in-reply"):
        errors.append(f'{where}.thinks must be "built-in" or "in-reply"')
    if entry.get("model") is not None and not isinstance(entry["model"], str):
        errors.append(f"{where}.model must be the name of a model")
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
    for flag in ("thinking", "budget_sentence", "cave_leak"):
        if not isinstance(data.get(flag, False), bool):
            errors.append(f"{flag} must be true or false")
    return errors


def _fit_errors(data):
    """A crew needs a square each, and every column needs a letter from A to Z."""
    size = data.get("grid_size", DEFAULTS["grid_size"])
    if _is_int(size) and size > MOST_COLUMNS:
        why = "since columns are lettered A to Z"
        return [f"grid_size can be at most {MOST_COLUMNS}, {why}"]
    pirates = data.get("pirates")
    crew = (
        len(pirates)
        if isinstance(pirates, list)
        else data.get("crew_size", DEFAULTS["crew_size"])
    )
    if not (_is_int(size) and size >= 1 and _is_int(crew)) or crew <= size * size:
        return []
    return [f"{crew} pirates can't each have a square on a grid of size {size}"]


def _problems(data):
    unknown = [
        f"{key} is not a config setting"
        for key in data
        if key not in DEFAULTS and key not in ("pirates", "prompt")
    ]
    return [
        *unknown,
        *(prompts.problems(data["prompt"]) if "prompt" in data else []),
        *_number_errors(data),
        *_fit_errors(data),
        *_crew_errors(data),
    ]


def _pirate(index, crew_size, entry):
    colour = entry.get("colour")
    return Pirate(
        personality=entry.get("personality", index % PERSONALITIES + 1),
        head_text=entry.get("head_text", str(index + 1)),
        colour=tuple(colour) if colour else _default_colour(index, crew_size),
        model=entry.get("model"),
        thinks=entry.get("thinks"),
    )


def parse_config(data):
    """A checked GameConfig from plain values, or a ConfigError naming each problem."""
    problems = _problems(data)
    if problems:
        raise ConfigError("; ".join(problems))
    settings = {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}
    entries = data.get("pirates", [{}] * settings["crew_size"])
    crew_size = len(entries)
    settings["crew_size"] = crew_size
    pirates = tuple(
        _pirate(index, crew_size, entry) for index, entry in enumerate(entries)
    )
    prompt = prompts.prompt_config(data.get("prompt", {}))
    return GameConfig(pirates=pirates, prompt=prompt, **settings)


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
