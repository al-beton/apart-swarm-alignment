"""The example games: a fixed set to look at after every change.

Each is a saved game in `examples/<name>/` plus its GIF, in a run folder like any
other, so every command works on it. `make examples` remakes them all. A change
to how a game plays or looks must remake them on purpose, because a test compares
them with what the code does now.

Implements: results/examples-folder, results/examples-small, results/examples-stay-true
"""

import shutil
from pathlib import Path

from treasure_island import saved_game, viewer

# Each example's config and seed. One line on what each shows is in the guide,
# examples/README.md.
EXAMPLES = {
    "silent": ("configs/silent.toml", 7),
    "stripes": ("configs/stripes.toml", 7),
    "scribe": ("configs/scribe.toml", 7),
    "small-crew": ("configs/small-crew.toml", 7),
}
REMAKE = "`make examples` remakes them, if the change is meant to show."


def stale(folder):
    """What in an example no longer matches what the code does now."""
    folder = Path(folder)
    different = saved_game.differences(folder)
    if viewer.gif(folder) != (folder / "game.gif").read_bytes():
        different.append("game.gif")
    if viewer.transcript(folder) != (folder / "transcript.md").read_text():
        different.append("transcript.md")
    return different


def problem(folder):
    """What a person needs to read if this example is stale, or None if it isn't."""
    if different := stale(folder):
        return f"{folder}: {', '.join(different)} no longer match. {REMAKE}"
    return None


def remake(name, root=Path()):
    """Play one example again from nothing, into `examples/<name>/`."""
    config_path, seed = EXAMPLES[name]
    folder = Path(root) / "examples" / name
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    config = saved_game.config_with_seed(Path(root) / config_path, seed)
    saved_game.write_saved(config, folder)
    (folder / "game.gif").write_bytes(viewer.gif(folder))
    viewer.write_transcript(folder)
    return folder


def main():
    for name in EXAMPLES:
        print(remake(name))


if __name__ == "__main__":
    main()
