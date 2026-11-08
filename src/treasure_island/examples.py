"""The example games: a fixed pair to look at after every change.

Each is a saved game in `examples/<name>/` plus its GIF, its `transcript.md` and its
game page `game.html`, in a run folder like any other, so every command works on it.
`llm-crew` is a real LLM crew and `stripes` the striping scripted pirates on the same
island. `make examples` replays `stripes` from nothing and redraws `llm-crew` from
its own game, since playing it again would ask real models (that takes a key and a
yes: `treasure-island run configs/llm-crew.toml --seed 7`). A change to how a game
plays or looks must remake them on purpose, because a test compares them with what
the code does now: `stripes` byte for byte, `llm-crew` by its recorded actions.

Implements: results/examples-folder, results/examples-small, results/examples-stay-true
"""

import shutil
from pathlib import Path

from treasure_island import replay, saved_game, viewer

# Each example's config and seed, in the order they're shown. One line on what each
# shows is in the guide, examples/README.md.
EXAMPLES = {
    "llm-crew": ("configs/llm-crew.toml", 7),
    "stripes": ("configs/stripes.toml", 7),
}
PLAYED_BY_MODELS = {"llm-crew"}  # replayed by its recorded actions, never re-asked
REMAKE = "`make examples` remakes them, if the change is meant to show."


def stale(folder):
    """What in an example no longer matches what the code does now."""
    folder = Path(folder)
    if folder.name in PLAYED_BY_MODELS:
        different = ["its recorded actions"] if replay.problem(folder) else []
    else:
        different = saved_game.differences(folder)
    if viewer.gif(folder) != (folder / "game.gif").read_bytes():
        different.append("game.gif")
    if viewer.transcript(folder) != (folder / "transcript.md").read_text():
        different.append("transcript.md")
    if viewer.slideshow_page(folder) != (folder / "game.html").read_text():
        different.append("game.html")
    return different


def draw(folder):
    """Write an example's GIF, transcript and game page from its own game."""
    (folder / "game.gif").write_bytes(viewer.gif(folder))
    viewer.write_transcript(folder)
    (folder / "game.html").write_text(viewer.slideshow_page(folder), encoding="utf-8")


def problem(folder):
    """What a person needs to read if this example is stale, or None if it isn't."""
    if different := stale(folder):
        return f"{folder}: {', '.join(different)} no longer match. {REMAKE}"
    return None


def remake(name, root=Path()):
    """Play one example again from nothing, into `examples/<name>/`.

    An example played by models is only redrawn from its own game, never re-asked.
    """
    config_path, seed = EXAMPLES[name]
    folder = Path(root) / "examples" / name
    if name in PLAYED_BY_MODELS:
        draw(folder)
        return folder
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    config = saved_game.config_with_seed(Path(root) / config_path, seed)
    saved_game.write_saved(config, folder)
    draw(folder)
    return folder


def main():
    for name in EXAMPLES:
        print(remake(name))


if __name__ == "__main__":
    main()
