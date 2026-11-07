# Results

Findings worth keeping, each with the games behind it. This guide has no `Implements:` line because nothing here may carry one; a row in `product/spec/results.md` homes these folders.

- **`sample-sweep-seeds/`:** where the treasure lands decides how well the silent crew scores. A sample showing the layout, from scripted games.

## Adding a result

1. Play the games with `uv run treasure-island run CONFIG --seed N`, and move their run folders from `runs/` into `results/<name>/`.
2. Write `results/<name>/README.md` with these four headings: `## Question`, `## What was run`, `## What it shows` and `## What it cost`. Take every number from the games' own logs.
3. Add its GIF, of whichever game shows it best: `uv run treasure-island render results/<name>/<game> --out results/<name>/game.gif`.
4. Add one line for it to this list. A test fails until you do.

The pull request's game comment then shows what it found, how each game ended and that GIF.

Every command works on a run folder here: `uv run treasure-island replay results/sample-sweep-seeds/small-crew-seed-1`, or `watch` and `render`. CI replays them all with no keys and no network. If a change to the game stops one replaying, CI fails, and deciding what to do about that result is part of the change.

## Results, examples and runs

- `results/` keeps findings: a question, the games that answer it and what they cost. Nobody remakes these.
- `examples/` is the fixed set of games to look at after every change, remade with `make examples` when a change is meant to show.
- `runs/` is everyday evidence: where a new game lands, and what experiments commit as they go.
