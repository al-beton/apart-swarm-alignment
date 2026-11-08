<!-- Implements: specs-and-docs/folder-guides -->
# Configs

One TOML file per kind of game: `treasure-island run configs/<name>.toml --seed N`. The seed isn't in the file, so one config can be played many times. `silent.toml`, `stripes.toml` and `scribe.toml` set every lever of the real game, seed included, for the reference games (`make reference-games`), and name the `brain` the crew plays with. `small-crew.toml` is for an example game. `coached.toml` is the stripes game with the coaching paragraph (`prompts/slots/extra/coaching.md`) at the end of the prompt; give its pirates a `model` to play an LLM arm that hears it. Every config names its `brain`; one that doesn't is refused.
