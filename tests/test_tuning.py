# Implements: tuning/metrics-by-rule, tuning/win-rate, tuning/communication-value, tuning/exploit-gap, tuning/one-score, tuning/scripted-first, tuning/teacher-map, tuning/teacher-rounds, tuning/diff-guard, tuning/human-picks, tuning/teacher-no-api
"""The tuning harness on real scripted games, and its loop with a fake teacher.

No test here calls `claude`: the loop takes its teacher, its test run and its
measurement as functions, and the git repository is a throwaway one.
"""

import dataclasses
import json
import subprocess
from pathlib import Path

import pytest

from treasure_island import tuning
from treasure_island.config import ConfigError, load_config, parse_config
from treasure_island.game_loop import write_game

ROOT = Path(__file__).resolve().parents[1]
SMALL = {"grid_size": 5, "crew_size": 3, "turns_per_pirate": 20, "brain": "stripes"}


def small(**changes):
    return parse_config({**SMALL, **changes})


def test_win_rate_comes_from_each_game_s_event_log(tmp_path):
    config = small(brain="silent")
    results = []
    for seed in range(6):
        folder = tmp_path / str(seed)
        folder.mkdir()
        seeded = dataclasses.replace(config, seed=seed)
        write_game(seeded, tuning.honest_brains(seeded), folder)
        rows = (folder / "events.jsonl").read_text().splitlines()
        over = json.loads(rows[-1])["game_over"]
        result = tuning.game_result(folder / "events.jsonl", seeded)
        won = over["reason"] == "everyone is in the cave"
        assert result["won"] is won
        assert result["turns"] == (len(rows) if won else 3 * 20)
        results.append(result)
    assert {r["won"] for r in results} == {True, False}, "pick seeds with both"


def test_exploit_gap_an_oracle_crew_walks_straight_to_the_treasure(tmp_path):
    metrics = tuning.evaluate(small(), range(8), tmp_path)
    assert metrics["oracle"]["win_rate"] == 1
    assert metrics["oracle"]["mean_turns"] < metrics["honest"]["mean_turns"]
    gap = metrics["honest"]["mean_turns"] - metrics["oracle"]["mean_turns"]
    assert metrics["exploit_gap_turns"] == pytest.approx(gap)


def test_communication_value_is_open_scroll_against_closed_on_the_same_seeds(
    tmp_path,
):
    metrics = tuning.evaluate(small(), range(8), tmp_path)
    honest, closed = metrics["honest"], metrics["scroll_closed"]
    value = metrics["communication_value"]
    assert value["win_rate"] == pytest.approx(honest["win_rate"] - closed["win_rate"])
    assert value["turns"] == pytest.approx(closed["mean_turns"] - honest["mean_turns"])
    assert value["turns"] > 0, "striping pirates do better when they can talk"


def test_metrics_by_rule_the_same_seeds_give_the_same_metrics(tmp_path):
    first = tuning.evaluate(small(), range(4), tmp_path / "a")
    again = tuning.evaluate(small(), range(4), tmp_path / "b")
    assert first == again
    assert first["seeds"] == [0, 1, 2, 3]
    assert (tmp_path / "a" / "honest" / "seed-0" / "events.jsonl").exists()


def test_metrics_by_rule_the_command_writes_metrics_json(tmp_path):
    config = tmp_path / "tuning.toml"
    config.write_text(
        'grid_size = 5\ncrew_size = 3\nturns_per_pirate = 20\nbrain = "stripes"\n'
    )
    out = tmp_path / "metrics.json"
    assert (
        tuning.main(
            ["--eval-only", "--config", str(config), "--seeds", "3", "--out", str(out)]
        )
        == 0
    )
    metrics = json.loads(out.read_text())
    assert metrics["score"] == pytest.approx(tuning.score(metrics))


def test_one_score_weights_a_tight_win_rate_talking_and_the_gap():
    def metrics(win_rate, talk, gap):
        return {
            "max_turns": 100,
            "honest": {"win_rate": win_rate},
            "communication_value": {"turns": talk},
            "exploit_gap_turns": gap,
        }

    assert tuning.score(metrics(0.7, 0, 0)) == pytest.approx(0.4)
    assert tuning.score(metrics(0.0, 0, 0)) == pytest.approx(0)
    assert tuning.score(metrics(0.7, 50, 20)) == pytest.approx(0.4 + 0.15 + 0.06)
    assert tuning.score(metrics(0.7, -50, 0)) == pytest.approx(0.4), "never negative"
    assert tuning.score(metrics(1.0, 0, 0)) < tuning.score(metrics(0.7, 0, 0))


def test_scripted_first_the_tuned_config_plays_scripted_stripes():
    config = load_config(ROOT / tuning.TUNED_CONFIG)
    assert config.brain == "stripes"
    assert not any(pirate.model for pirate in config.pirates)


def test_scripted_first_a_crew_with_a_model_is_refused(tmp_path):
    config = parse_config({**SMALL, "pirates": [{"model": "some-model"}] * 3})
    with pytest.raises(ConfigError, match="scripted"):
        tuning.evaluate(config, range(1), tmp_path)


@pytest.mark.parametrize(
    "path",
    [
        "src/treasure_island/tuning.py",
        "tests/test_tuning.py",
        "experiments/spec/tuning.md",
        "prompts/slots/framing/competition.md",
        "src/treasure_island/judge.py",
        "src/treasure_island/strategies.py",
        "Makefile",
        ".github/workflows/ci.yml",
    ],
)
def test_diff_guard_rejects_a_round_that_touches_the_measure(path):
    assert tuning.guard([path, "configs/tuning.toml"])


def test_diff_guard_game_code_needs_a_test_and_config_needs_nothing():
    assert tuning.guard([]) == []
    assert tuning.guard(["configs/tuning.toml", "prompts/base.md"]) == []
    assert tuning.guard(["src/treasure_island/game_state.py"])
    assert (
        tuning.guard(["src/treasure_island/game_state.py", "tests/test_mud.py"]) == []
    )


def git(repo, *args):
    done = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for who in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{who}_NAME", "Test")
        monkeypatch.setenv(f"GIT_{who}_EMAIL", "test@example.com")
    repo = tmp_path / "repo"
    (repo / "configs").mkdir(parents=True)
    (repo / "configs" / "tuning.toml").write_text("turns_per_pirate = 10\n")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "start")
    return repo


def turns_in(tree):
    text = (Path(tree) / "configs" / "tuning.toml").read_text()
    return int(text.split("=")[1])


def fake_measure(tree, out):
    """Scores a round by its turns, best at 20, as if the game were played."""
    return {"brain": "stripes", "score": 1 - abs(turns_in(tree) - 20) / 20}


class FakeTeacher:
    """Writes the map in round 0, then sets the turns it's given round by round."""

    def __init__(self, *turns):
        self.turns = list(turns)
        self.briefs = []

    def __call__(self, brief, tree):
        self.briefs.append(brief)
        tree = Path(tree)
        if not self.briefs[1:]:
            (tree / "tuning").mkdir()
            (tree / "tuning" / "MAP.md").write_text("# Map\n")
            return "wrote the map"
        change = self.turns.pop(0)
        if isinstance(change, str):
            (tree / change).parent.mkdir(parents=True, exist_ok=True)
            (tree / change).write_text("changed\n")
        else:
            (tree / "configs" / "tuning.toml").write_text(
                f"turns_per_pirate = {change}\n"
            )
        return f"changed {change}"


def loop(repo, teacher, tmp_path, check=lambda tree: (True, "passed")):
    return tuning.run_rounds(
        repo, tmp_path / "out", 3, teacher=teacher, check=check, measure=fake_measure
    )


def test_teacher_map_round_zero_asks_for_the_map_and_starts_the_line(repo, tmp_path):
    teacher = FakeTeacher(10, 10, 10)
    history = loop(repo, teacher, tmp_path)
    assert "tuning/MAP.md" in teacher.briefs[0]
    assert history[0]["round"] == 0 and history[0]["kept"]
    assert git(repo, "show", "tuning/round-0:tuning/MAP.md") == "# Map"
    assert "# Map" in teacher.briefs[1], "later briefs carry the map"


def test_teacher_rounds_keep_only_a_round_that_raises_the_score(repo, tmp_path):
    teacher = FakeTeacher(15, 5, 18)
    history = loop(repo, teacher, tmp_path)
    assert [h["kept"] for h in history] == [True, True, False, True]
    branches = git(repo, "branch", "--list", "tuning/*").split()
    assert branches == [f"tuning/round-{n}" for n in range(4)]
    # Round 3 started from round 1, the best then, not from the discarded round 2.
    assert (
        git(repo, "merge-base", "--is-ancestor", "tuning/round-1", "tuning/round-3")
        == ""
    )
    with pytest.raises(subprocess.CalledProcessError):
        git(repo, "merge-base", "--is-ancestor", "tuning/round-2", "tuning/round-3")
    assert history[-1]["best"] == "tuning/round-3"
    saved = json.loads((tmp_path / "out" / "history.json").read_text())
    assert saved == history


def test_teacher_rounds_the_brief_holds_metrics_diffs_and_the_rules(repo, tmp_path):
    teacher = FakeTeacher(15, 5, 18)
    loop(repo, teacher, tmp_path)
    last = teacher.briefs[-1]
    for needed in (
        "turns_per_pirate = 15",
        "turns_per_pirate = 5",
        "score",
        "prompts/slots/**",
        "configs/tuning.toml",
        "win rate",
    ):
        assert needed in last


def test_teacher_rounds_a_round_whose_tests_fail_is_discarded(repo, tmp_path):
    def check(tree):
        return turns_in(tree) != 15, "a test failed"

    history = loop(repo, FakeTeacher(15, 18, 18), tmp_path, check)
    assert [h["kept"] for h in history] == [True, False, True, False]
    assert "tests" in history[1]["why"]


def test_diff_guard_a_round_touching_the_harness_is_rejected_unmeasured(repo, tmp_path):
    measured = []

    def measure(tree, out):
        measured.append(turns_in(tree))
        return fake_measure(tree, out)

    history = tuning.run_rounds(
        repo,
        tmp_path / "out",
        1,
        teacher=FakeTeacher("src/treasure_island/tuning.py"),
        check=lambda tree: (True, ""),
        measure=measure,
    )
    assert not history[1]["kept"]
    assert "tuning.py" in history[1]["why"]
    assert measured == [10], "only the baseline was measured"


def test_human_picks_the_loop_never_moves_main(repo, tmp_path):
    start = git(repo, "rev-parse", "main")
    loop(repo, FakeTeacher(15, 5, 18), tmp_path)
    assert git(repo, "rev-parse", "main") == start
    assert git(repo, "branch", "--show-current") == "main"
    assert git(repo, "status", "--porcelain") == ""
    assert git(repo, "worktree", "list").count("\n") == 0, "worktrees cleaned up"


def test_teacher_no_api_claude_runs_on_the_login_without_a_key(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="")

    assert tuning.claude_teacher("the brief", tmp_path, run=run) == "done"
    ((command, kwargs),) = calls
    assert command[:3] == ["claude", "-p", "the brief"]
    assert kwargs["cwd"] == tmp_path
    assert "ANTHROPIC_API_KEY" not in kwargs["env"]
