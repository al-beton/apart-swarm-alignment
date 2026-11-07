# Implements: agents/refusals-noted
"""Every reply that isn't a valid action is noted: in the story, the manifest and the run."""

import json

import pytest

from treasure_island import cli, saved_game
from treasure_island.saved_game import Models

DIG = json.dumps({"tool": "dig", "arguments": {}})
CONFIG = """
grid_size = 3
turns_per_pirate = 2
brain = "silent"

[[pirates]]
model = "fake/thinker"

[[pirates]]
"""


class FakeModel:
    """A backend that answers from a list, then repeats the last answer."""

    def __init__(self, *answers):
        self.answers = list(answers)

    def __call__(self, request):
        answer = self.answers.pop(0) if len(self.answers) > 1 else self.answers[0]
        return answer, 0.0


def yes():
    return True


@pytest.fixture
def toml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "thinker.toml"
    path.write_text(CONFIG)
    return path


def played(toml, *answers):
    model = FakeModel(*answers)
    folder = saved_game.play_saved(toml, 0, models=Models(model, agree=yes))
    lines = (folder / "story.txt").read_text().splitlines()
    pirate_1 = [line for line in lines if " pirate-1 at " in line]
    manifest = json.loads((folder / "manifest.json").read_text())
    return pirate_1, manifest


def test_refusals_noted_the_story_says_a_reply_was_not_valid_and_the_turn_went_on(toml):
    pirate_1, _ = played(toml, "let me think", DIG)
    assert "gave 1 reply that wasn't a valid action, then dug at" in pirate_1[0]


def test_refusals_noted_the_story_says_when_the_turn_passed(toml):
    pirate_1, _ = played(toml, "no idea")
    assert (
        "gave 2 replies that weren't valid actions, so its turn passed" in pirate_1[0]
    )


def test_refusals_noted_a_turn_with_only_good_replies_says_nothing_of_it(toml):
    pirate_1, manifest = played(toml, DIG)
    assert all("valid action" not in line for line in pirate_1)
    assert "refused_replies" not in manifest


def test_refusals_noted_the_manifest_counts_them_for_each_pirate(toml):
    _, manifest = played(toml, "no idea")
    assert manifest["refused_replies"] == {"pirate-1": 4}  # 2 turns, 2 tries each


def test_refusals_noted_the_run_command_ends_with_a_warning(toml, monkeypatch, capsys):
    monkeypatch.setattr(saved_game, "backend_for", lambda model: FakeModel("no idea"))
    argv = ["run", str(toml), "--seed", "0", "--no-watch", "--yes"]
    assert cli.main(argv) == 0
    err = capsys.readouterr().err
    assert "4 replies weren't valid actions" in err
    assert "pirate-1 gave 4" in err


def test_refusals_noted_a_run_with_none_has_no_warning(toml, monkeypatch, capsys):
    monkeypatch.setattr(saved_game, "backend_for", lambda model: FakeModel(DIG))
    cli.main(["run", str(toml), "--seed", "0", "--no-watch", "--yes"])
    assert "valid action" not in capsys.readouterr().err


class CostlyModel:
    """A backend whose every reply costs the whole default $1 cap."""

    def __init__(self, answer):
        self.answer = answer

    def __call__(self, request):
        return self.answer, 1.0


def test_refusals_noted_a_turn_the_cap_stopped_still_counts_its_bad_replies(toml):
    model = CostlyModel("no idea")
    folder = saved_game.play_saved(toml, 0, models=Models(model, agree=yes))
    manifest = json.loads((folder / "manifest.json").read_text())
    assert "stopped" in manifest
    assert manifest["refused_replies"] == {"pirate-1": 1}


def test_refusals_noted_a_run_the_cap_stopped_warns_of_them(toml, monkeypatch, capsys):
    monkeypatch.setattr(saved_game, "backend_for", lambda model: CostlyModel("no idea"))
    cli.main(["run", str(toml), "--seed", "0", "--no-watch", "--yes"])
    assert "pirate-1 gave 1" in capsys.readouterr().err
