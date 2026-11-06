"""Named figures: the report's graphics, each built from a committed run.

A figure is the viewer's GIF of one committed run, written next to a Markdown
file holding its two lines: the command that rebuilds it from that run, and
the command that plays the game again into a new run folder. Rebuilding needs
no keys and no network, because it reads only what's in the repository.

Implements: figures/named-figures, figures/two-lines, figures/rerun-matches
"""

import dataclasses
import json
import tomllib
from pathlib import Path

from treasure_island import viewer


@dataclasses.dataclass(frozen=True)
class Figure:
    run: str  # the committed run folder it's built from
    config: str  # the config that plays that game again
    seed: int


FIGURES = {
    "sweep-game": Figure("runs/sweep-seed-5", "configs/sweep.toml", 5),
    "counter-game": Figure("runs/counter-seed-1", "configs/counter.toml", 1),
}


def lines(name):
    """The figure's two lines: rebuild it for free, or rerun the game for real."""
    figure = FIGURES[name]
    return (
        f"make figure NAME={name}",
        f"treasure-island run {figure.config} --seed {figure.seed}",
    )


def rerun_mismatch(name):
    """Why the rerun command wouldn't play the committed game, or None if it would."""
    figure = FIGURES[name]
    saved = json.loads(Path(figure.run, "config.json").read_text())
    wanted = {**tomllib.loads(Path(figure.config).read_text()), "seed": figure.seed}
    differ = sorted(key for key in saved | wanted if saved.get(key) != wanted.get(key))
    if differ:
        return f"{name}: {figure.config} --seed {figure.seed} differs from {figure.run} in {', '.join(differ)}."
    return None


def build(name, out="figures"):
    """Write the figure and its two lines under `out`; return the GIF's path."""
    if mismatch := rerun_mismatch(name):
        raise ValueError(mismatch)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    gif = viewer.render(FIGURES[name].run, out / f"{name}.gif")
    rebuild, rerun = lines(name)
    (out / f"{name}.md").write_text(
        f"![{name}]({name}.gif)\n\n"
        f"Rebuild it from the committed run, with no keys: `{rebuild}`\n\n"
        f"Play the game again into a new run folder: `{rerun}`\n"
    )
    return gif
