# Examples

Games to look at after every change, and to open first if you're new here, played under the v2 rules: digging gives readings, any action can say a line for free, and `go_to` walks without asking. Each folder is a saved game plus its `game.gif` and `transcript.md`, which holds every turn in full: read [`silent/transcript.md`](silent/transcript.md) first, `story.txt` for the short version, or watch it with `uv run treasure-island watch examples/<name>`. `make examples` remakes them, and CI fails if one no longer matches what the code does. This guide has no `Implements:` line because nothing here may carry one; a row in `product/spec/results.md` homes these folders.

- **`silent/`:** three silent pirates each search the grid alone, ignoring their readings and never saying anything, walk to the nearest square they haven't seen dug and go into the cave once they stand on it: the baseline a talking crew should beat.
- **`noisy/`:** four silent pirates on a 6 by 6 grid whose readings are off by up to 2 either way, so the story shows readings that aren't the true distance, and the walks under `go_to` orders are longer.
- **`small-crew/`:** two pirates on a small grid, so a whole game fits on one screen.
