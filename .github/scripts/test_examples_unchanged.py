# Implements: ci/examples-remade-in-ci, runs/played-at
"""The examples check, in a throwaway git repository holding one example."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("examples_unchanged.py")
MANIFEST = {"cost_usd": 0, "finished_at": "t1", "started_at": "t0"}


def git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def one_example(tmp_path):
    folder = tmp_path / "examples" / "silent"
    folder.mkdir(parents=True)
    (folder / "manifest.json").write_text(json.dumps(MANIFEST, indent=2))
    (folder / "config.json").write_text('{"seed": 7}')
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", ".")
    git(tmp_path, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    return folder


def check(root):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )


def test_examples_remade_in_ci_only_the_manifests_times_may_change(tmp_path):
    folder = one_example(tmp_path)
    later = {**MANIFEST, "finished_at": "t9", "started_at": "t8"}
    (folder / "manifest.json").write_text(json.dumps(later, indent=2))
    assert check(tmp_path).returncode == 0
    # The new times are put back, so the check leaves nothing to commit.
    assert json.loads((folder / "manifest.json").read_text()) == MANIFEST


def test_examples_remade_in_ci_any_other_change_fails_and_says_how_to_fix_it(
    tmp_path,
):
    folder = one_example(tmp_path)
    (folder / "config.json").write_text('{"seed": 7, "thinking": false}')
    costly = {**MANIFEST, "cost_usd": 1}
    (folder / "manifest.json").write_text(json.dumps(costly, indent=2))
    (folder / "new.txt").write_text("left behind")
    result = check(tmp_path)
    assert result.returncode == 1
    for path in ("config.json", "manifest.json", "new.txt"):
        assert f"examples/silent/{path}" in result.stdout
    assert "make examples" in result.stdout


def test_played_at_examples_check_ignores_the_commit_and_dirty(tmp_path):
    folder = one_example(tmp_path)
    later = {**MANIFEST, "commit": "abc123", "dirty": False, "started_at": "t8"}
    (folder / "manifest.json").write_text(json.dumps(later, indent=2))
    assert check(tmp_path).returncode == 0
    assert json.loads((folder / "manifest.json").read_text()) == MANIFEST
