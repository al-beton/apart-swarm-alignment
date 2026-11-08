# Three pirates, 4x4, the rewritten prompt

## Played

2026-11-08, 02:22 to 02:30 UTC, by Claude at Al's request, to try the rewritten prompt (#191) on the game the other 4x4 games used. The code was `main` at commit `8bc5f54e5`, with no local changes. It includes #187, so the pirates' reasoning is saved.

## Settings

Three pirates, 4x4 grid, 10 turns each, seed 3 (treasure at (1, 1), B3), thinking on with `thinking_tokens = 4096`, every pirate on `adaption/deepseek-v4-flash` (the config's `brain = "silent"` is unused, since every pirate names a model). The prompt states the shared score plainly and gives no advice on how to play.

## What it cost

0.007989 credits for 22 model calls. No reply was rejected.

## What it showed

Nobody wrote a plan. Pirate-2 dug up the treasure at B3, then wrote "P2: OPEN CAVE AT B3. Everyone come to B3 and enter." before going in, with no coaching. Its reasoning says why. Pirate-3 read the note, walked over and went in. Pirate-1 read the scroll too late to get back, and spent its last turn walking towards the cave. Score 280, against 140 (original prompt) and 250 (coaching paragraph); one game each.

The reasoning also showed two prompt problems. Each pirate's list of earlier turns still gave squares as (x, y) while the rest said A2 (issue 190), and pirate-3's reasoning noticed: "there's a discrepancy". And every earlier turn carries its full reasoning, about 95% of the text a pirate reads by mid-game. Al decided to keep that.

## Replaying it

Check out `8bc5f54e5`, copy `run/` to `runs/crew-newprompt-seed-3`, then `uv run treasure-island replay runs/crew-newprompt-seed-3`. Today's code changes the prompt, so it doesn't replay there; issue 215 is about that.
