# Implements: paper/built-two-ways
"""The build's images: every image the paper shows, copied into the build folder
at the path the text names, plus a PNG still beside each GIF, because LaTeX
can't show an animation. The still is the GIF's last frame, the game as it ended.

Usage: python -m paper.stills paper/paper.md paper/build
"""

import shutil
import sys
from pathlib import Path

from PIL import Image

from paper.check import images


def write_stills(skeleton, build):
    """Copy each image under `build`, with a PNG for each GIF; return the paths written."""
    written = []
    for image in images(skeleton):
        source = Path(image)
        target = Path(build, source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target)
        written.append(target)
        if source.suffix == ".gif":
            still = target.with_suffix(".png")
            with Image.open(source) as frames:
                frames.seek(frames.n_frames - 1)
                frames.convert("RGB").save(still)
            written.append(still)
    return written


if __name__ == "__main__":
    write_stills(*sys.argv[1:3])
