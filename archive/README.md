# Archive

Real model games, kept exactly as they were played, each with an `ABOUT.md` saying where it came from: when, at which commit, with which local changes, the model and settings, what it cost and what it showed. This guide has no `Implements:` line because nothing here may carry one; a row in `product/spec/results.md` homes these folders.

Each game is `archive/<name>/`, holding:
- `run/`, the run folder as the game wrote it: `story.txt` (read this first), `pirates-log.txt` (the scroll), `events.jsonl`, `replies.jsonl` (every request and reply, word for word), `config.json` and `manifest.json`
- `game.gif`
- `ABOUT.md`

These games were played on older code. CI doesn't replay them, and most won't replay on today's code, because the prompt has changed since. Each `ABOUT.md` says how to replay it. `spike-changes.diff` holds the local changes the 2026-11-07 games were played with.

All of them used `adaption/deepseek-v4-flash` through Adaption's Responses API, at the provider's default temperature. Costs are in Adaption credits, which the manifests label `cost_usd`.

Squares in the 2026-11-07 games are written (x, y): x grows east, y grows south, and (0, 0) is the north-west corner. In the 2026-11-08 game the pirates are told chess names, A1 in the south-west, but the story still writes (x, y).

## Games

- **`2026-11-07-one-pirate-3x3/`:** the first working LLM game. One pirate searches sensibly and runs out of turns two squares from the treasure.
- **`2026-11-07-one-pirate-treasure-underfoot/`:** the treasure is under the landing square, so the pirate digs it up and goes in within two turns.
- **`2026-11-07-crew-4x4-original-prompt/`:** three pirates, and nobody ever writes on the scroll. The finder goes into the cave without telling anyone. Score 140.
- **`2026-11-07-crew-4x4-shared-score-paragraph/`:** the same game with one paragraph spelling out the shared score. Plans appear on turn 1, and the finder announces the cave before going in. Score 250.
- **`2026-11-07-crew-6x6-clashing-plans/`:** three plans written at once, by rows and by columns. Each pirate switches to another's plan, and nobody reaches the far corner. Score 0.
- **`2026-11-07-five-pirates-15x15/`:** five pirates agree on a plan by rows, but 50 turns each can't cover 225 squares. Score 0.
- **`2026-11-08-crew-4x4-new-prompt/`:** the 4x4 game again on the rewritten prompt, with the pirates' reasoning saved. The finder announces the cave with no coaching. Score 280.
