# One pirate, 3x3, after the reasoning-budget fix

## Played

2026-11-07, about 12:12 UTC, by Al with Claude (the "AI LLM API implementor" session), as part of a spike to get LLM pirates playing. The code was `main` at commit `3f77bf7c0`, plus one local change from `../spike-changes.diff`: the Adaption backend asked for `max_output_tokens` of 300 + 1024 rather than 300. Without that change, deepseek spent its whole 300-token reply reasoning and returned nothing, so an earlier try of this same game passed on 4 of its 5 turns. That earlier try's folder wasn't kept.

## Settings

One pirate, 3x3 grid, 5 turns, seed 1 (treasure at (0, 2)), thinking off, model `adaption/deepseek-v4-flash`.

## What it cost

0.000904 credits for 6 model calls (`run/manifest.json`).

## What it showed

The pirate searched sensibly: dig (0, 0), move east, dig (1, 0), move south, dig (1, 1). It ran out of turns two squares from the treasure, for a score of 0. One reply came back empty even with the bigger budget, and the retry handled it.

## Replaying it

On a checkout of commit `3f77bf7c0` (for example `git worktree add ../replay 3f77bf7c0`), copy this game's `run/` to `runs/2026-11-07-one-pirate-3x3`, then run `uv run treasure-island replay runs/2026-11-07-one-pirate-3x3`. Apply no patch: this game's prompt is the commit's own. Replaying never calls a model, so the backend changes in `../spike-changes.diff` don't matter here. Checked on 2026-11-08: it rebuilds both logs and the story byte-identical.
