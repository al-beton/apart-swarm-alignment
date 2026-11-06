# Implements: tooling/package-and-cli
"""The command `pyproject.toml` installs runs, without needing anything else."""

import subprocess
import sys
from pathlib import Path


def test_package_and_cli_help_runs_from_the_installed_command():
    command = Path(sys.executable).with_name("treasure-island")
    done = subprocess.run(
        [str(command), "--help"], capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stderr
    assert "treasure-island" in done.stdout
