# Implements: specs-and-docs/readme-commands-run
"""Every command in the README's feature list works, so a stale entry fails CI."""

import re
import shlex
import shutil
from pathlib import Path

import pytest

from treasure_island import cli

ROOT = Path(__file__).resolve().parents[1]
_SECTION = "## What you can do today"
_ROW = re.compile(r"^\|[^|]*\|\s*`([^`]+)`\s*\|\s*$", re.MULTILINE)


def feature_commands():
    """The command cell of each row in the README's feature table."""
    readme = (ROOT / "README.md").read_text()
    if _SECTION not in readme:
        return []
    section = readme.split(_SECTION, 1)[1].split("\n## ", 1)[0]
    return _ROW.findall(section)


def make_targets():
    return set(re.findall(r"^([\w-]+):", (ROOT / "Makefile").read_text(), re.MULTILINE))


def test_readme_commands_run_the_feature_list_exists():
    assert feature_commands()


@pytest.mark.parametrize("command", feature_commands())
def test_readme_commands_run_each_feature_command_works(command, tmp_path, monkeypatch):
    words = shlex.split(command)
    if words[0] == "make":
        assert set(words[1:]) <= make_targets(), command
        return
    assert words[:3] == ["uv", "run", "treasure-island"], (
        f"Can't check {command!r}: feature commands are make targets or "
        "uv run treasure-island ..."
    )
    for folder in ("configs", "runs"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    monkeypatch.chdir(tmp_path)
    # A person watches `run` in a browser; here it only has to work.
    arguments = [*words[3:], "--no-watch"] if words[3] == "run" else words[3:]
    try:
        code = cli.main(arguments)
    except SystemExit as exit:  # argparse's --help
        code = exit.code
    assert code == 0, command
