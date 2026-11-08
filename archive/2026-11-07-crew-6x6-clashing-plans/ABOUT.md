# Three pirates, 6x6, treasure in the far corner

## Played

2026-11-07, between about 12:30 and 13:20 UTC, by Al with Claude. The code was `main` at commit `3f77bf7c0` plus the local changes in `../spike-changes.diff`: the reasoning budget raised to + 4096, the shared-score paragraph (see `2026-11-07-crew-4x4-shared-score-paragraph`), and, for the last sitting only, an Adaption client with `max_retries=6, timeout=180`.

It was played in three sittings. The first stopped on a network failure (a DNS error, `APIConnectionError`), the second on `APITimeoutError`. Each restart reused every reply already received, so the game continued exactly where it stopped. `run/` is the folder of the last sitting, which holds every reply.

## Settings

Three pirates, 6x6 grid, 20 turns each, seed 20 (treasure at (5, 5), the corner furthest from where they land), thinking on but not saved (see #187), `adaption/deepseek-v4-flash`.

## What it cost

0.009367 credits for the last sitting's 66 model calls. The two earlier sittings stopped before writing a manifest, so their cost (a few thousandths of a credit) wasn't recorded.

## What it showed

Talking isn't enough to coordinate. Pirate-1 wrote a plan by rows using (row, col). Pirate-2 wrote one by columns using (x, y), and pirate-3 another by columns. Pirate-2 then wrote "UNIFY on ROW plan", while pirate-1 wrote "P1 CONFIRMS column plan": each switched to the other's plan. By the end they were listing the squares they'd dug and asking each other to cover the gaps. Nobody reached (5, 5), and the score was 0. The prompt never said which way the coordinates run, so the pirates guessed. 2 moves hit the north edge. No reply came back empty with the + 4096 budget.

## Replaying it

Commit `3f77bf7c0` plus `../spike-changes.diff` as it stands, copied to `runs/far-seed-20`.
