<!-- Implements: specs-and-docs/folder-guides -->
# Experiments

What we set out to find with the game, written down before each experiment runs. `spec/` has one file per experiment, each statement a question or hypothesis with a name. Findings notes live here too.

## Tabling experiment one

Once experiment one's games are committed under `runs/cave-leak/<arm>-seed-<n>/`, one command tables them from their `events.jsonl` alone, with no model calls:

```sh
uv run python -m treasure_island.cave_leak_table runs/cave-leak
```

It prints Markdown that pastes into the findings note unchanged. There's a row per game: arm, seed, the turn the first pirate went into the cave (or never), how many got in, the score, the turn the cave leak fired (or never) and who it told. Then each arm's means and its mean difference from the control game of the same seed. Folders that aren't a finished game are listed as skipped, with why.
