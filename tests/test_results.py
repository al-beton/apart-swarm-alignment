# Implements: results/result-folder, results/results-are-runs, results/results-listed, results/results-stay-checkable, results/sample-result, research/results-have-a-place, results/result-gif
"""Results have one home: each a folder of run folders that anyone can replay."""

import os
import socket
from pathlib import Path

import pytest

from treasure_island import cli, replay

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "results"
SAMPLE = "sample-sweep-seeds"
HEADINGS = ["## Question", "## What was run", "## What it shows", "## What it cost"]
RUN_FILES = {"config.json", "events.jsonl", "manifest.json", "replies.jsonl"}


def names():
    """Every committed result, found from the folder so a new one can't be missed."""
    return sorted(path.name for path in FOLDER.iterdir() if path.is_dir())


def run_folders(name):
    return sorted(path for path in (FOLDER / name).iterdir() if path.is_dir())


ALL_RUNS = [folder for name in names() for folder in run_folders(name)]


def test_result_folder_each_holds_run_folders_and_says_what_it_found():
    assert names()
    for name in names():
        assert run_folders(name), name
        guide = (FOLDER / name / "README.md").read_text()
        for heading in HEADINGS:
            assert heading in guide, f"{name} has no '{heading}'"


@pytest.mark.parametrize("folder", ALL_RUNS, ids=lambda path: path.name)
def test_results_are_runs_with_the_same_files(folder):
    assert RUN_FILES <= {path.name for path in folder.iterdir()}


def test_results_are_runs_the_same_commands_work(tmp_path, capsys):
    out = tmp_path / "game.gif"
    assert cli.main(["render", str(ALL_RUNS[0]), "--out", str(out)]) == 0
    assert out.read_bytes()[:3] == b"GIF"


def listed():
    lines = (FOLDER / "README.md").read_text().splitlines()
    return [
        line.split("`")[1].rstrip("/") for line in lines if line.startswith("- **`")
    ]


def test_results_listed_in_the_index_exactly_once_each():
    assert sorted(listed()) == names()


CHECKED_RESULTS = [
    ROOT / name for name in replay.CHECKED if name.startswith("results/")
]


@pytest.mark.parametrize("folder", CHECKED_RESULTS, ids=lambda path: path.name)
def test_results_stay_checkable_replaying_with_no_keys_or_network(
    folder, monkeypatch, capsys
):
    for name in list(os.environ):
        if name.endswith("_API_KEY"):
            monkeypatch.delenv(name)

    def no_network(*args, **kwargs):
        raise AssertionError("a socket was opened")

    monkeypatch.setattr(socket, "socket", no_network)
    assert cli.main(["replay", str(folder)]) == 0


def test_sample_result_is_a_scripted_game_that_cost_nothing():
    assert SAMPLE in names()
    guide = (FOLDER / SAMPLE / "README.md").read_text()
    assert "$0" in guide
    for folder in run_folders(SAMPLE):
        story = (folder / "story.txt").read_text()
        # The numbers the guide quotes come from the games' own logs.
        score = story.splitlines()[-1].split("Score ")[1].split(",")[0]
        assert f"Score {score}" in guide, folder.name


@pytest.mark.parametrize("guide", ["AGENTS.md", ".agents/skills/team/SKILL.md"])
def test_results_have_a_place_the_team_is_told_where_results_go(guide):
    text = (ROOT / guide).read_text()
    for folder in ("results/", "examples/", "runs/"):
        assert folder in text, f"{guide} doesn't mention {folder}"


def test_result_gif_each_result_has_one_under_2_mb():
    results = [path for path in (ROOT / "results").iterdir() if path.is_dir()]
    assert results
    for result in results:
        gif = result / "game.gif"
        assert gif.read_bytes().startswith(b"GIF"), result
        assert gif.stat().st_size < 2_000_000, result


def test_results_stay_checkable_each_result_has_a_game_on_the_list():
    for name in names():
        games = [
            path.parent for path in (ROOT / "results" / name).rglob("events.jsonl")
        ]
        if all(replay.first_rules(game) for game in games):
            continue  # first-rules games can't replay under the v2 rules
        assert any(item.startswith(f"results/{name}/") for item in replay.CHECKED), name
