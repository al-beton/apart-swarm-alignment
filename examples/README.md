# Examples

Games to look at after every change, and to open first if you're new here. Each folder is a saved game plus its `game.gif`: read `story.txt`, or watch it with `uv run treasure-island watch examples/<name>`. `make examples` remakes them, and CI fails if one no longer matches what the code does. This guide has no `Implements:` line because nothing here may carry one; a row in `product/spec/results.md` homes these folders.

- **`s-sweep/`:** three pirates walk an S across the grid together and find the treasure, with moves to spare.
- **`stripes/`:** three pirates each dig their own rows and write when they're blocked; the one that finds the treasure writes where it is, and the crew reads it and goes in.
- **`small-crew/`:** two pirates on a small grid, so a whole game fits on one screen.
