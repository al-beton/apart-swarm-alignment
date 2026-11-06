# Implements: ci/ci-minutes, ci/one-gate, ci/ci-runs-everything, ci/no-model-calls, tooling/how-we-work, specs-and-docs/folder-guides, agent-setup/reuse-old-work
"""The gate, and the few files a newcomer starts from, are what the spec says."""

import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"


def workflow():
    return yaml.safe_load((WORKFLOWS / "blocking-checks.yml").read_text())


def runs():
    """The `run` lines of the gate."""
    steps = workflow()["jobs"]["blocking-checks"]["steps"]
    return [str(s["run"]) for s in steps if "run" in s]


def test_ci_minutes_the_gate_is_one_job():
    # Every gating check is a step of one job, whose name is the status
    # deliver.py's merge waits for.
    assert list(workflow()["jobs"]) == ["blocking-checks"]
    assert [p.name for p in WORKFLOWS.glob("*.yml")] == ["blocking-checks.yml"]


def test_ci_minutes_tests_run_in_parallel_with_cached_dependencies():
    assert "pytest -n auto" in (ROOT / "Makefile").read_text()
    steps = workflow()["jobs"]["blocking-checks"]["steps"]
    uv = next(s for s in steps if "setup-uv" in s.get("uses", ""))
    assert uv["with"]["enable-cache"] is True


def test_ci_minutes_the_gate_runs_every_check():
    gate = " ".join(runs())
    for check in ("pr_gate.py", "make lint", "make test", "make spec-check"):
        assert check in gate, check
    # Each step runs something that exists: a Makefile target make knows, and
    # the scripts the steps name.
    for run in runs():
        if run.startswith("make "):
            target = run.split()[1]
            dry = subprocess.run(
                ["make", "-n", target],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            assert dry.returncode == 0, f"{run}: {dry.stderr}"
    for path in re.findall(r"[\w./-]+\.py", gate):
        assert (ROOT / path).is_file(), path


def test_ci_minutes_newer_runs_cancel_older_ones_and_drafts_wait():
    flow = workflow()
    # Only pull request runs cancel: main's runs after a merge must finish,
    # or a second merge would make the first look as if main failed.
    cancel = flow["concurrency"]["cancel-in-progress"]
    assert cancel == "${{ github.event_name == 'pull_request' }}"
    # A draft run would only be skipped, so it gets a group of its own: in the
    # pull request's group it would cancel a ready run, running or queued.
    group = flow["concurrency"]["group"]
    assert (
        "!github.event.pull_request.draft && github.event.pull_request.number" in group
    )
    assert "|| github.run_id" in group
    assert "draft" in flow["jobs"]["blocking-checks"]["if"]


def test_no_model_calls_no_secret_but_the_github_token():
    """No workflow reads an API key: the only secret is the GitHub token."""
    for path in WORKFLOWS.glob("*.yml"):
        secrets = set(re.findall(r"secrets\.(\w+)", path.read_text()))
        assert secrets <= {"GITHUB_TOKEN"}, (path, secrets)


def test_how_we_work_is_five_lines_and_points_agents_to_agents_md():
    readme = (ROOT / "README.md").read_text()
    work = readme.split("## How we work", 1)[1].split("\n## ", 1)[0]
    assert len(re.findall(r"^\d+\. ", work, re.MULTILINE)) == 5
    assert "AGENTS.md" in work


def test_folder_guides_every_top_level_folder_has_a_readme():
    hidden = {".agents", ".claude", ".github", ".venv", ".cache"}
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    folders = {path.split("/")[0] for path in tracked if "/" in path} - hidden
    assert folders
    for folder in sorted(folders):
        assert (ROOT / folder / "README.md").is_file(), folder


def test_reuse_old_work_links_the_commit_and_names_what_to_copy():
    agents = (ROOT / "AGENTS.md").read_text()
    section = agents.split("## Reusing the old work", 1)[1].split("\n## ", 1)[0]
    assert "al-beton/something-to-lose-apart-ai-collusion" in section
    assert "24961e54c" in section
    for name in (
        "backends.py",
        "cache.py",
        "runner.py",
        "manifest.py",
        "provenance.py",
        "estimate.py",
        "debrief.py",
        "leisure.py",
        "conditions/free_time.py",
        "report/",
        "deploy/",
    ):
        assert name in section, name
