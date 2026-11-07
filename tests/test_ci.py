# Implements: assets/sheet-on-every-pr, ci/examples-remade-in-ci, ci/ci-minutes, ci/one-gate, ci/ci-runs-everything, ci/no-model-calls, tooling/how-we-work, specs-and-docs/folder-guides, agent-setup/reuse-old-work, treasure-island/gif-per-change, results/examples-on-every-pr, results/result-on-its-pr
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
    # deliver.py's merge waits for. No other workflow runs a job of that name.
    assert list(workflow()["jobs"]) == ["blocking-checks"]
    for path in WORKFLOWS.glob("*.yml"):
        if path.name != "blocking-checks.yml":
            assert "blocking-checks" not in yaml.safe_load(path.read_text())["jobs"]


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


def test_examples_remade_in_ci_the_gate_runs_the_check():
    gate = runs()
    assert "make examples-check" in gate
    assert gate.index("make install") < gate.index("make examples-check")
    makefile = (ROOT / "Makefile").read_text()
    target = makefile.split("\nexamples-check:", 1)[1].split("\n\n", 1)[0]
    assert "examples" in target
    assert "examples_unchanged.py" in target


def test_no_model_calls_no_secret_but_the_github_token():
    """No workflow reads an API key: the only secret is the GitHub token."""
    for path in WORKFLOWS.glob("*.yml"):
        secrets = set(re.findall(r"secrets\.(\w+)", path.read_text()))
        assert secrets <= {"GITHUB_TOKEN"}, (path, secrets)


def sheet_workflow():
    return yaml.safe_load((WORKFLOWS / "asset-sheet.yml").read_text())


def sheet_steps():
    return sheet_workflow()["jobs"]["asset-sheet"]["steps"]


def test_sheet_on_every_pr_runs_on_pull_request_and_never_pull_request_target():
    # PyYAML reads the bare key `on` as true.
    triggers = sheet_workflow()[True]
    assert list(triggers) == ["pull_request"]
    assert "types" not in (triggers["pull_request"] or {})


def test_sheet_on_every_pr_can_only_write_pull_requests():
    assert sheet_workflow()["permissions"] == {"pull-requests": "write"}
    assert "permissions" not in sheet_workflow()["jobs"]["asset-sheet"]


def test_sheet_on_every_pr_runs_no_code_from_the_branch():
    # No step uses an action, so nothing checks out the branch or runs from it.
    assert not [step for step in sheet_steps() if "uses" in step]


def test_sheet_on_every_pr_skips_forks_and_never_gates():
    job = sheet_workflow()["jobs"]["asset-sheet"]
    assert "head.repo.full_name == github.repository" in job["if"]
    assert "blocking-checks" not in sheet_workflow()["jobs"]


def test_sheet_on_every_pr_shows_the_latest_commit_s_sheet_in_one_comment():
    step = sheet_steps()[0]
    run = step["run"]
    assert step["env"]["SHA"] == "${{ github.event.pull_request.head.sha }}"
    assert "raw.githubusercontent.com/$REPO/$SHA/assets/sheet.png" in run
    # It finds its own comment by a marker, so it never edits another
    # workflow's comment and a later push updates this one.
    assert "<!-- asset-sheet -->" in run
    assert "--method PATCH" in run


def test_sheet_on_every_pr_shows_the_catwalk_beside_the_sheet_from_the_same_commit():
    run = sheet_steps()[0]["run"]
    assert "raw.githubusercontent.com/$REPO/$SHA/assets/catwalk.gif" in run
    # A branch from before the catwalk gets the sheet alone, not a broken image.
    assert '--head --output /dev/null "$catwalk"' in run
    # One table row, so the two sit side by side.
    assert re.search(r"\| !\[[^]]*\]\(\$url\) \| !\[[^]]*\]\(\$catwalk\) \|", run)


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


def gif_workflow():
    return yaml.safe_load((WORKFLOWS / "game-gif.yml").read_text())


def gif_runs(job):
    steps = gif_workflow()["jobs"][job]["steps"]
    return " ".join(str(step.get("run", "")) for step in steps)


def test_gif_per_change_plays_a_whole_game_and_renders_it_from_that_commit():
    runs = gif_runs("render")
    assert "treasure-island run configs/silent.toml --seed 7 --no-watch" in runs
    assert "treasure-island render" in runs
    steps = gif_workflow()["jobs"]["render"]["steps"]
    assert any("upload-artifact" in step.get("uses", "") for step in steps)
    assert (ROOT / "configs/silent.toml").is_file()
    # By default a pull request checks out a merge with its base, which isn't
    # the commit the comment names.
    checkout = steps[0]
    assert "checkout" in checkout["uses"]
    assert checkout["with"]["ref"] == "${{ github.event.pull_request.head.sha }}"


def test_gif_per_change_never_blocks_merging():
    # It's its own workflow, and nothing in the gate waits for it.
    assert "gif" not in " ".join(workflow()["jobs"])
    assert "game-gif" not in (WORKFLOWS / "blocking-checks.yml").read_text()


def test_gif_per_change_keeps_write_access_away_from_the_branch_code():
    flow = gif_workflow()
    assert flow["permissions"] == {"contents": "read"}
    jobs = flow["jobs"]
    assert "pull-requests" not in jobs["render"].get("permissions", {})
    assert jobs["comment"]["permissions"]["pull-requests"] == "write"
    assert jobs["comment"]["needs"] == "render"
    uses = [step.get("uses", "") for step in jobs["comment"]["steps"]]
    assert not any("checkout" in use for use in uses)


def test_gif_per_change_updates_the_same_comment_on_a_later_push():
    runs = gif_runs("comment")
    assert "<!-- game-gif -->" in runs
    assert "PATCH" in runs
    assert "gh pr comment" in runs
    # Only one comment comes out of two pushes close together.
    assert gif_workflow()["concurrency"]["cancel-in-progress"] is True


def test_gif_per_change_links_the_gif_of_that_commit():
    runs = gif_runs("comment")
    assert "GIF_URL" in runs
    assert "SHA" in runs
    env = gif_workflow()["jobs"]["comment"]["steps"][0]["env"]
    assert "needs.render.outputs" in env["GIF_URL"]


def test_examples_on_every_pr_shows_each_gif_inline_with_its_ending():
    runs = gif_runs("comment")
    assert "raw.githubusercontent.com/$REPO/$SHA/examples/$name" in runs
    assert "$raw/story.txt" in runs
    assert "![$name]($raw/game.gif)" in runs
    assert "tail -n 1" in runs


def test_examples_on_every_pr_reads_the_commit_without_running_its_code():
    job = gif_workflow()["jobs"]["comment"]
    assert job["permissions"]["contents"] == "read"
    assert job["permissions"]["pull-requests"] == "write"
    assert not any("checkout" in step.get("uses", "") for step in job["steps"])


def test_examples_on_every_pr_lists_examples_from_that_commit():
    runs = gif_runs("comment")
    assert "contents/examples?ref=$SHA" in runs
    assert 'select(.type == \\"dir\\")' in runs or 'select(.type == "dir")' in runs


def comment_script():
    steps = gif_workflow()["jobs"]["comment"]["steps"]
    return next(step["run"] for step in steps if "run" in step)


def test_result_on_its_pr_shows_summary_endings_and_gif():
    script = comment_script()
    assert "$raw/README.md" in script
    assert "$raw/game.gif" in script
    assert "![$result]($raw/game.gif)" in script
    assert "story.txt" in script
    assert "tail -n 1" in script


def test_result_on_its_pr_reads_only_what_the_pull_request_changed():
    script = comment_script()
    assert "repos/$REPO/pulls/$PR/files" in script
    assert "results/" in script
    # Only committed files at this commit, and still no checkout in this job.
    assert "raw.githubusercontent.com/$REPO/$SHA/results/$result" in script


def test_result_on_its_pr_has_no_section_without_a_result():
    script = comment_script()
    assert 'if [ -n "$results" ]' in script
    assert "**Results in this pull request**" in script
    # A result the pull request removes has nothing to show.
    assert 'curl --silent --fail --head --output /dev/null "$raw/README.md"' in script


def test_result_on_its_pr_finds_the_section_a_result_calls_what_it_shows():
    # The heading the comment looks for is the one every result must have.
    assert "## What it shows" in comment_script()
    guide = (ROOT / "results/README.md").read_text()
    assert "`## What it shows`" in guide
