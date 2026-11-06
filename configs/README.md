<!-- Implements: specs-and-docs/folder-guides -->
# Configs

One TOML file per kind of game: `treasure-island run configs/<name>.toml --seed N`. The seed isn't in the file, so one config can be played many times. `s-sweep.toml` and `say-a-number.toml` set every lever of the real game, seed included, for the reference games (`make reference-games`), and name the `brain` the crew plays with. `small-crew.toml` is for an example game. A config with a `brain` plays the real game; one without plays the walking skeleton.
