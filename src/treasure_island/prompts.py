"""The pirates' system prompt: one base file with a few named slots filled in.

The base (`prompts/base.md` by default) is the rules and actions, written once
and tuned on its own. It holds the game's numbers as `{crew_size}`,
`{grid_size}`, `{turns_per_pirate}`, `{last_column}`, `{score_in_cave}`,
`{score_per_turn_left}`, `{failed_tries}`, `{say_chars}` and `{reading_rule}`
(the sentence on how far off a reading can be), and each
slot as `{framing}`, `{rules}`, `{disclosure}`, `{identity}` or `{extra}` alone
on its own line; `{extra}` is a paragraph of its own at the very end. An
experiment arm picks one variant per slot, the file
`prompts/slots/<slot>/<variant>.md`, which may use the same numbers; `none` drops
the slot's line entirely, so an unset slot leaves no blank line behind, and an
unset `{extra}` leaves none at the end either.

Relative paths are read from the repository root, not the working directory, so
a game plays the same prompt wherever it's started from.

Implements: treasure-island/extra-paragraph, prompts/base-and-slots, prompts/base-file, prompts/slots, prompts/unknown-slot, prompts/prompt-recorded
"""

import dataclasses
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "prompts/base.md"
SLOTS = ("framing", "rules", "disclosure", "identity", "extra")
NONE = "none"
_VARIANT = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclasses.dataclass(frozen=True)
class PromptConfig:
    """Which base file and which variant of each slot a game's pirates are told."""

    base: str = BASE
    slots: dict = dataclasses.field(default_factory=lambda: dict.fromkeys(SLOTS, NONE))


def _path(name):
    return ROOT / name


def _variant_path(slot, variant):
    return _path(f"prompts/slots/{slot}/{variant}.md")


def problems(block):
    """What's wrong with a config's `[prompt]` block, each problem named."""
    if not isinstance(block, dict):
        return ["prompt must be a table"]
    errors = [
        f"prompt.{key} is not a prompt setting"
        for key in block
        if key not in ("base", "slots")
    ]
    base = block.get("base", BASE)
    if not isinstance(base, str) or not _path(base).is_file():
        errors.append(f"prompt.base {base!r} is not a file")
    slots = block.get("slots", {})
    if not isinstance(slots, dict):
        return [*errors, "prompt.slots must be a table"]
    for slot, variant in slots.items():
        if slot not in SLOTS:
            errors.append(f"prompt.slots.{slot} is not a slot: use {', '.join(SLOTS)}")
        elif variant != NONE and not (
            isinstance(variant, str)
            and _VARIANT.match(variant)
            and _variant_path(slot, variant).is_file()
        ):
            errors.append(
                f"prompt.slots.{slot} has no variant {variant!r}: "
                f"it needs prompts/slots/{slot}/{variant}.md"
            )
    return errors


def prompt_config(block):
    """A checked block as a PromptConfig, every slot named (see `problems`)."""
    slots = {**dict.fromkeys(SLOTS, NONE), **block.get("slots", {})}
    return PromptConfig(block.get("base", BASE), slots)


def base_sha256(prompt):
    """The hash of the base file, so a run says which version of it played."""
    return hashlib.sha256(_path(prompt.base).read_bytes()).hexdigest()


def render(prompt, tail="", **numbers):
    """The base with its numbers and slots filled in, ready for a pirate to read.

    `tail` is what the game adds after the base (the cave leak's rule, the thinking
    budget); the `extra` paragraph comes after even that, so it's always last.
    """
    texts = {
        slot: ""
        if variant == NONE
        else _variant_path(slot, variant)
        .read_text(encoding="utf-8")
        .strip()
        .format(**numbers)
        for slot, variant in prompt.slots.items()
    }
    extra = texts.get("extra", "")
    texts["extra"] = ""  # its spot in the base only marks the end; it goes last
    empty = {f"{{{slot}}}" for slot, text in texts.items() if not text}
    base = _path(prompt.base).read_text(encoding="utf-8")
    lines = [line for line in base.splitlines() if line.strip() not in empty]
    rules = "\n".join(lines).format(**numbers, **texts).rstrip() + tail
    return f"{rules}\n\n{extra}" if extra else rules
