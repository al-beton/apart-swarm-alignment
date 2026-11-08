# Prompts

What the pirates read, word for word. `base.md` is the system prompt's fixed base: the rules and actions, with the game's numbers in braces (`{crew_size}`, `{grid_size}`, `{turns_per_pirate}`, `{last_column}`, `{score_in_cave}`, `{score_per_turn_left}`, `{failed_tries}`, `{say_chars}`, and `{reading_rule}`, the sentence on how far off a reading can be) and one line per slot (`{framing}`, `{rules}`, `{disclosure}`, `{identity}`, and `{extra}`, a paragraph of its own at the very end). Each slot's variants are `slots/<slot>/<variant>.md`, which may use the same numbers in braces, and a config picks one per slot, `none` (the default) leaving that line out:

```toml
[prompt]
base = "prompts/base.md"
[prompt.slots]
framing = "competition"
rules = "tools-only"
disclosure = "free"          # or "zeroes-score"
identity = "ai-research-study"
extra = "coaching"           # how to swarm: split the search, say where the cave is, plan from turn 1
```

The `disclosure/*` variants offer a way to tell the game's designers that doesn't exist yet: they wait for a reporting tool, so don't use them in an arm before it's built.

A new variant is a new file; no code changes. A run's manifest keeps the prompt it rendered, so a reader sees what the pirates were told. This guide has no `Implements:` line because nothing under `prompts/` may carry one; rows in `product/spec/prompts.md` home these files.
