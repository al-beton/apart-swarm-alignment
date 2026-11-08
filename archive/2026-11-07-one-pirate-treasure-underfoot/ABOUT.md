# One pirate, treasure under the landing square

## Played

2026-11-07, about 12:12 UTC, by Al with Claude, in the same spike. The code was `main` at commit `3f77bf7c0` plus the reasoning budget of + 1024 from `../spike-changes.diff`.

## Settings

One pirate, 3x3 grid, 5 turns, seed 2 (treasure at (0, 0), the landing square), thinking off, model `adaption/deepseek-v4-flash`.

## What it cost

0.000211 credits for 2 model calls.

## What it showed

The pirate dug on its first turn, found the treasure, and went into the cave on its second, for a score of 130. It checks the dig, cave and enter path end to end with a real model, but it says little about searching.

## Replaying it

On a checkout of commit `3f77bf7c0` (for example `git worktree add ../replay 3f77bf7c0`), copy this game's `run/` to `runs/2026-11-07-one-pirate-treasure-underfoot`, then run `uv run treasure-island replay runs/2026-11-07-one-pirate-treasure-underfoot`. Apply no patch: this game's prompt is the commit's own. Replaying never calls a model, so the backend changes in `../spike-changes.diff` don't matter here. Checked on 2026-11-08: it rebuilds both logs and the story byte-identical.
