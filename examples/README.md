# Examples

Games to look at after every change, and to open first if you're new here. Each folder is a saved game plus its `game.gif` and `transcript.md`, which holds every turn in full: read [`stripes/transcript.md`](stripes/transcript.md) first, `story.txt` for the short version, or watch it with `uv run treasure-island watch examples/<name>`. `make examples` remakes them, and CI fails if one no longer matches what the code does. This guide has no `Implements:` line because nothing here may carry one; a row in `product/spec/results.md` homes these folders.

- **`silent/`:** three silent pirates each search the grid alone, never writing or reading, and go into the cave once they stand on it: the baseline a talking crew should beat.
- **`stripes/`:** three pirates each dig their own rows and write when they're blocked; the one that finds the treasure writes where it is, and the crew reads it and goes in.
- **`scribe/`:** three scribes search like silent pirates but write what each dig found, and where the cave is before going in, so the scroll fills with notes and the GIF shows pirates writing.
- **`small-crew/`:** two pirates on a small grid, so a whole game fits on one screen.
