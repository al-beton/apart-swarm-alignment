"""Fail if remaking the examples changed anything in examples/ but the manifests' times.

Run it after `make examples` (`make examples-check` does both). A manifest whose
only change is `started_at` and `finished_at` is put back as committed, so a clean
check leaves nothing to commit. Anything else, a new file included, is listed with
how to fix it, and the check fails.

Implements: ci/examples-remade-in-ci
"""

import json
import subprocess
import sys

TIMES = ("started_at", "finished_at")


def git(*args):
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def changed():
    """Every path under examples/ that differs from what's committed."""
    lines = git("status", "--porcelain", "--untracked-files=all", "--", "examples")
    return [line[3:] for line in lines.splitlines()]


def only_times(path):
    """Whether this manifest differs from the committed one only in its times."""
    if not path.endswith("/manifest.json"):
        return False
    try:
        before = json.loads(git("show", f"HEAD:{path}"))
        with open(path, encoding="utf-8") as file:
            after = json.load(file)
    except (subprocess.CalledProcessError, OSError, ValueError):
        return False
    for manifest in (before, after):
        for key in TIMES:
            manifest.pop(key, None)
    return before == after


def main():
    times = [path for path in changed() if only_times(path)]
    if times:
        git("checkout", "--", *times)
    left = changed()
    if not left:
        return 0
    print("make examples changed what's committed in examples/:")
    for path in left:
        print(f"  {path}")
    print("Run make examples and commit what it changes, in this pull request.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
