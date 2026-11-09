# Worlds: findings

<!-- Implements: natural-leak/counts-table -->

The question, the worlds and what's measured are in `experiments/spec/worlds.md`. Games are in `results/worlds/<world>-seed-<n>/`. The table is pirate-1's games per world, counted by rule from each game's `events.jsonl` and `judge.json`; refresh it with the command below; the paper's results section for the worlds takes the same markers and is added to the same command once its games are committed:

```sh
uv run treasure-island worlds-table results/worlds --write experiments/worlds/findings.md paper/sections/results/worlds.md
```

`uv run treasure-island worlds-table results/worlds --games` lists the folders behind every count.

<!-- worlds-table -->
The worlds wave's games aren't committed yet.
<!-- /worlds-table -->
