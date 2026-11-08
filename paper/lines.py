# Implements: paper/figures-carry-their-lines
"""Each named figure's two lines, for the build to put under it.

Writes `figure-lines.json` into the build folder: the rebuild command and the
rerun command of every named figure the paper shows, from the registry
(`treasure_island.figures.lines`). Pandoc reads it as metadata, and
`include.lua` adds the lines to each figure's caption, so they're never copied
by hand and can't go stale.

Usage: python -m paper.lines paper/paper.md paper/build
"""

import json
import sys
from pathlib import Path

from paper.check import images
from treasure_island.figures import FIGURES, lines


def write_lines(skeleton, build):
    """Write the shown figures' lines into `build`; return the file written."""
    shown = sorted(
        {
            Path(image).stem
            for image in images(skeleton)
            if image.startswith("figures/") and Path(image).stem in FIGURES
        }
    )
    # As code spans: pandoc reads metadata as Markdown, which would turn a
    # command's `--seed` into a dash.
    found = {name: [f"`{line}`" for line in lines(name)] for name in shown}
    target = Path(build, "figure-lines.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"figure_lines": found}, indent=2) + "\n")
    return target


if __name__ == "__main__":
    write_lines(*sys.argv[1:3])
