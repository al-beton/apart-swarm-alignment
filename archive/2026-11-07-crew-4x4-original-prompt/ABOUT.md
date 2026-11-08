# Three pirates, 4x4, the original prompt

## Played

2026-11-07, about 12:16 UTC, by Al with Claude. The code was `main` at commit `3f77bf7c0` plus the reasoning budget of + 1024 from `../spike-changes.diff`. The prompt was main's at that commit, which did state the shared score: "Your crew scores 100 for every pirate that gets into the cave, plus 10 for each turn it had left after going in."

## Settings

Three pirates, 4x4 grid, 10 turns each, seed 3 (treasure at (1, 1)), thinking off, every pirate on `adaption/deepseek-v4-flash`.

## What it cost

0.005955 credits for 36 model calls. It took about 7 minutes, at about 12 seconds per reply.

## What it showed

Nobody ever wrote on the scroll. The pirates read it 7 times and found it empty every time. Pirate-2 dug up the treasure on game turn 13 with both others close by, and went into the cave on turn 16 without telling anyone. The other two kept digging until their turns ran out. Score 140. One turn passed on bad replies.

## Replaying it

On a checkout of commit `3f77bf7c0` (for example `git worktree add ../replay 3f77bf7c0`), copy this game's `run/` to `runs/2026-11-07-crew-4x4-original-prompt`, then run `uv run treasure-island replay runs/2026-11-07-crew-4x4-original-prompt`. Apply no patch: this game's prompt is the commit's own. Replaying never calls a model, so the backend changes in `../spike-changes.diff` don't matter here. Checked on 2026-11-08: it rebuilds both logs and the story byte-identical.
