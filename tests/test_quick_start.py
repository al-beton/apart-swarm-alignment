# Implements: treasure-island/one-line-replay, treasure-island/python-stack
"""The README's first commands work, exactly as written, with no keys."""

import os
import re
import shlex
import shutil
import socket
from pathlib import Path

import yaml

from treasure_island import cli

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/al-beton/apart-swarm-alignment.git"


def readme():
    return (ROOT / "README.md").read_text()


def quick_start():
    """The commands in the README's quick start, in order."""
    section = readme().split("## Quick start", 1)[1].split("\n## ", 1)[0]
    block = re.search(r"```bash\n(.*?)```", section, flags=re.DOTALL).group(1)
    return block.strip().splitlines()


def test_one_line_replay_comes_first_in_the_readme():
    headings = re.findall(r"^## (.+)$", readme(), flags=re.MULTILINE)
    assert headings[0] == "Quick start"


def test_one_line_replay_starts_with_a_clone_and_needs_one_more_command():
    clone, enter, show = quick_start()
    assert clone == f"git clone {REPOSITORY}"
    assert enter == "cd apart-swarm-alignment"
    assert show.startswith("uv run treasure-island show ")


def test_one_line_replay_writes_a_gif_and_a_page_with_no_keys_or_network(
    tmp_path, monkeypatch, capsys
):
    for folder in ("configs", "examples"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    monkeypatch.chdir(tmp_path)
    for name in os.environ:
        if name.endswith("_API_KEY"):
            monkeypatch.delenv(name)

    def no_network(*args, **kwargs):
        raise AssertionError("the quick start opened a socket")

    monkeypatch.setattr(socket, "socket", no_network)
    words = shlex.split(quick_start()[-1])
    assert cli.main(words[3:]) == 0
    printed = capsys.readouterr().out
    gif, page = printed.split()[-2:]
    assert Path(gif).read_bytes().startswith(b"GIF")
    assert "<html" in Path(page).read_text().lower()


def test_one_line_replay_ci_runs_that_exact_command():
    flow = yaml.safe_load((ROOT / ".github/workflows/blocking-checks.yml").read_text())
    steps = flow["jobs"]["blocking-checks"]["steps"]
    assert quick_start()[-1] in [str(step.get("run")) for step in steps]


def test_python_stack_the_quick_start_needs_only_uv():
    section = readme().split("## Quick start", 1)[1].split("\n## ", 1)[0]
    assert "uv" in section
    assert "docs.astral.sh/uv" in section
