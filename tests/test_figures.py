# Implements: figures/named-figures, figures/two-lines, figures/rerun-matches, figures/figures-published
"""Named figures rebuild from committed runs, carry their two lines, and CI publishes them."""

import os
import socket
from pathlib import Path

import pytest
import yaml
from PIL import Image

from treasure_island import cli, figures, viewer

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def offline(monkeypatch):
    """No keys and no sockets."""
    for name in list(os.environ):
        if name.endswith("_API_KEY"):
            monkeypatch.delenv(name)

    def no_network(*args, **kwargs):
        raise AssertionError("a socket was opened")

    monkeypatch.setattr(socket, "socket", no_network)


def test_named_figures_build_offline_from_committed_runs(offline, tmp_path, capsys):
    assert cli.main(["figure", "silent-game", "--out", str(tmp_path)]) == 0
    gif = tmp_path / "silent-game.gif"
    assert str(gif) in capsys.readouterr().out
    records = viewer.records_in(ROOT / "runs/silent-seed-7")
    frames = sum(len(viewer.walk_steps(records, turn)) for turn in range(len(records)))
    assert Image.open(gif).n_frames == frames


def test_named_figures_every_figure_builds_and_an_unknown_name_fails(
    offline, tmp_path, capsys
):
    assert cli.main(["figure", "--all", "--out", str(tmp_path)]) == 0
    for name in figures.FIGURES:
        assert (tmp_path / f"{name}.gif").exists()
    assert cli.main(["figure", "no-such-figure", "--out", str(tmp_path)]) == 1
    assert "no-such-figure" in capsys.readouterr().err


def test_two_lines_sit_next_to_the_figure(offline, tmp_path):
    cli.main(["figure", "silent-game", "--out", str(tmp_path)])
    lines = (tmp_path / "silent-game.md").read_text()
    assert "make figure NAME=silent-game" in lines
    assert "uv run treasure-island run configs/silent.toml --seed 7" in lines


def test_rerun_matches_every_committed_run_without_spending(offline):
    for name in figures.FIGURES:
        assert figures.rerun_mismatch(name) is None, name


def test_rerun_matches_catches_a_config_that_differs(monkeypatch):
    wrong = figures.Figure("runs/silent-seed-7", "configs/stripes.toml", 7)
    monkeypatch.setitem(figures.FIGURES, "wrong", wrong)
    assert "brain" in figures.rerun_mismatch("wrong")
    off_by_one = figures.Figure("runs/silent-seed-7", "configs/silent.toml", 8)
    monkeypatch.setitem(figures.FIGURES, "off-by-one", off_by_one)
    assert "seed" in figures.rerun_mismatch("off-by-one")


def test_figures_published_as_an_artifact_by_the_gate():
    flow = yaml.safe_load((ROOT / ".github/workflows/blocking-checks.yml").read_text())
    steps = flow["jobs"]["blocking-checks"]["steps"]
    assert any(s.get("run") == "make figures" for s in steps)
    upload = next(s for s in steps if "upload-artifact" in s.get("uses", ""))
    assert upload["with"]["path"] == "figures/"
    assert "figures/" in (ROOT / ".gitignore").read_text().splitlines()
