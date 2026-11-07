"""Named figures: the report's graphics, each built from a committed run.

A figure is the viewer's GIF of one committed run, written next to a Markdown
file holding its two lines: the command that rebuilds it from that run, and
the command that plays the game again into a new run folder. Rebuilding needs
no keys and no network, because it reads only what's in the repository.

Implements: figures/named-figures, figures/two-lines, figures/rerun-matches
"""

import dataclasses
import json
from pathlib import Path

from treasure_island import viewer
from treasure_island.config import parse_config
from treasure_island.saved_game import config_with_seed


@dataclasses.dataclass(frozen=True)
class Figure:
    run: str  # the committed run folder it's built from
    config: str  # the config that plays that game again
    seed: int


FIGURES = {
    "s-sweep-game": Figure("runs/s-sweep-seed-7", "configs/s-sweep.toml", 7),
    "stripes-game": Figure("examples/stripes", "configs/stripes.toml", 7),
}


def lines(name):
    """The figure's two lines: rebuild it for free, or rerun the game for real."""
    figure = FIGURES[name]
    return (
        f"make figure NAME={name}",
        f"uv run treasure-island run {figure.config} --seed {figure.seed}",
    )


def rerun_mismatch(name):
    """Why the rerun command wouldn't play the committed game, or None if it would.

    Both sides go through the parser, because a run's `config.json` holds every
    lever and default while the file it was played from names only some.
    """
    figure = FIGURES[name]
    saved = parse_config(json.loads(Path(figure.run, "config.json").read_text()))
    wanted = config_with_seed(figure.config, figure.seed)
    differ = [
        field.name
        for field in dataclasses.fields(saved)
        if getattr(saved, field.name) != getattr(wanted, field.name)
    ]
    if differ:
        return (
            f"{name}: {figure.config} --seed {figure.seed} differs from "
            f"{figure.run} in {', '.join(differ)}."
        )
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
