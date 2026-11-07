<!-- Implements: specs-and-docs/folder-guides, tuning/teacher-map -->
# Tuning

What the tuning loop's teacher writes for later rounds. Round 0 of `make tune` adds `MAP.md` here, on its `tuning/round-0` branch: the knobs a config can set, how to play and score a game, and what the logs record. The loop and its scoring are in `src/treasure_island/tuning.py`; its output (briefs, what the teacher said, metrics, `history.json`) goes to `.cache/tuning/`, which git ignores.
