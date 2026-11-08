# Five pirates, 15x15

## Played

2026-11-07, between about 12:55 and 14:20 UTC, by Al with Claude. The code was `main` at commit `3f77bf7c0` plus the reasoning budget of + 4096 and the shared-score paragraph from `../spike-changes.diff`, without the retry change. The first sitting stopped on a network failure after 6 replies, and the restart reused them.

## Settings

Five pirates, 15x15 grid, 50 turns each, seed 6 (treasure at (12, 9)), thinking on but not saved (see #187), `adaption/deepseek-v4-flash`.

## What it cost

0.096983 credits for the second sitting's 282 model calls (the free estimate's ceiling was 0.42). The 6 calls of the first sitting weren't recorded. It took over an hour.

## What it showed

Four of the five wrote a plan in their first turns, two by rows and one by columns, until pirate-5 settled it: "ALL use ROW plan". The crew agreed, unlike in the 6x6 game. But each pirate's strip was 45 squares, which takes about 90 turns of moving and digging, and they had 50. The treasure lay at the far end of pirate-5's rows, and was never dug up. Score 0. Of the 250 turns, 122 were moves, 73 were reads (mostly "nothing new"), 47 were digs and 4 were writes. 15 moves hit the north edge, because the pirates read (x, y) as (row, col). No square was dug twice, but pirates often walked back over dug squares. Even with the + 4096 budget, 16 of the 282 replies came back empty. All but one were saved by asking once more, and 1 turn passed.

## Replaying it

On a checkout of commit `3f77bf7c0` (for example `git worktree add ../replay 3f77bf7c0`), first apply only the prompt change, `git apply archive/shared-score-paragraph.diff` (the patch file is in this repository's `archive/`), which adds the shared-score paragraph this game's pirates were given. Then copy this game's `run/` to `runs/2026-11-07-five-pirates-15x15` and run `uv run treasure-island replay runs/2026-11-07-five-pirates-15x15`. Replaying never calls a model, so the backend changes in `../spike-changes.diff` don't matter here. Checked on 2026-11-08: it rebuilds both logs and the story byte-identical.
