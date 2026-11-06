# Runs

One folder per game played, in `s-sweep-seed-7/`'s shape: `story.txt` (the one to read), `pirates-log.txt`, `events.jsonl`, `replies.jsonl`, `config.json` and `manifest.json`. `reference-s-sweep/` and `reference-say-a-number/` are the real game's reference games, with `events.jsonl`, `story.txt` (read this one), `pirates-log.txt` and `config.json`, and they replay like any other run. Committed ones are evidence, homed by a row in the spec that needs them; `scratch/` and `smoke/` stay uncommitted. This guide has no `Implements:` line because nothing under `runs/` may carry one.
