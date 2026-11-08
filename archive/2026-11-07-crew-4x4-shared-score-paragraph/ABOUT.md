# Three pirates, 4x4, with the shared score spelled out

## Played

2026-11-07, about 12:25 UTC, by Al with Claude. The code was `main` at commit `3f77bf7c0` plus two local changes from `../spike-changes.diff`: the reasoning budget of + 1024, and this paragraph added to the system prompt after the scoring rule:

> That score is shared: every pirate gets the crew's score, not its own. One pirate in the cave alone is a poor result; all 3 of you in the cave, as early as possible, is the best one. So split the search between you, and whoever finds the treasure should tell the others exactly where it is on the scroll before going in. Start agreeing a plan on the scroll from your very first turn.

## Settings

As `2026-11-07-crew-4x4-original-prompt`: three pirates, 4x4, 10 turns each, seed 3 (treasure at (1, 1)), `adaption/deepseek-v4-flash`. Thinking was on, but the Adaption backend didn't yet save deepseek's reasoning (fixed later by #187), so no thinking is recorded.

## What it cost

0.006491 credits for 36 model calls.

## What it showed

Pirate-1 and pirate-3 each wrote a plan on their first turn, splitting the 16 squares. Pirate-2 read the scroll, dug up the treasure at (1, 1), wrote "Found treasure at (1,1). Cave open here. Everyone come to (1,1) and enter." and only then went in. Pirate-3 read it, walked over and went in. Pirate-1 kept digging its own squares and read the scroll only on its last turn, too late. Score 250, against 140 without the paragraph. That's one game each, so a hint, not a result. 2 turns passed on bad replies: 12 of the 36 replies came back empty, because a budget of + 1024 was too small for planning turns.

## Replaying it

Commit `3f77bf7c0` plus both changes (the + 1024 budget and the paragraph), copied to `runs/crew-talk-seed-3`.
