# Prompts

What the pirates read, word for word. `base.md` is the system prompt's fixed base: the rules and actions, with the game's numbers in braces (`{crew_size}`, `{grid_size}`, `{turns_per_pirate}`, `{last_column}`, `{score_in_cave}`, `{score_per_turn_left}`, `{failed_tries}`) and one line per slot (`{framing}`, `{rules}`, `{disclosure}`, `{identity}`). Each slot's variants are `slots/<slot>/<variant>.md`, and a config picks one per slot, `none` (the default) leaving that line out:

```toml
[prompt]
base = "prompts/base.md"
[prompt.slots]
framing = "competition"
rules = "tools-only"
disclosure = "free"          # or "zeroes-score"
identity = "ai-research-study"
```

A new variant is a new file; no code changes. A run's manifest keeps the prompt it rendered, and replay uses that, so editing `base.md` never changes an old game. This guide has no `Implements:` line because nothing under `prompts/` may carry one; rows in `product/spec/prompts.md` home these files.
