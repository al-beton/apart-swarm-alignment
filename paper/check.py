# Implements: paper/one-source, paper/sections-bind-to-evidence, paper/sprint-rules-checked
"""The paper's contract with the repository, checked before every build.

Errors (exit 1, the build stops):
- a section the skeleton lists is missing, or a file under sections/results/
  isn't listed, so no text is silently left out;
- a results section has no marker (`<!-- experiment: name -->` or
  `<!-- result: name -->` on its first lines), or its marker names an
  experiment spec or a result folder that isn't in the repository;
- an image is neither a named figure (`figures/<name>.<ext>`, name in the
  registry) nor a committed file. Committed means git tracks it: a file that
  only exists locally would be missing from a clean clone.

Warnings (printed, the build goes on): the abstract outside the sprint's word
range, or the main text past the sprint's page cap. Both limits are in the
skeleton's front matter (`abstract-words`, `max-pages`). The page count is the
page of the `main-end` label in the LaTeX .aux, so it's known only after
`make paper-pdf`.

Usage: python -m paper.check paper/paper.md [paper/build/paper.aux]
"""

import re
import subprocess
import sys
from functools import cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ABSTRACT_WORDS = (150, 250)
DEFAULT_MAX_PAGES = 4
MAIN_END = re.compile(r"\\newlabel\{main-end\}\{\{[^}]*\}\{(\d+)\}")
FRONT = re.compile(r"(?:\s*<!--.*?-->)*\s*---\n(.*?)\n---\n", re.DOTALL)
INCLUDE = re.compile(r"```\{\.include\}\n(.*?)```", re.DOTALL)
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
MARKER = re.compile(r"<!--\s*(experiment|result):\s*([a-z0-9-]+)\s*-->")
MARKER_LINES = 5  # the marker sits in the file's first lines, with the Implements line
EVIDENCE = {
    "experiment": lambda name: f"experiments/spec/{name}.md",
    "result": lambda name: f"results/{name}/README.md",
}


@cache
def committed(root):
    """The files git tracks under `root`: what a clean clone would hold. Outside
    a repository, every file there is."""
    try:
        listed = subprocess.run(
            ["git", "ls-files"], cwd=root, capture_output=True, text=True, check=True
        ).stdout.split("\n")
    except (OSError, subprocess.CalledProcessError):
        listed = [p.relative_to(root).as_posix() for p in Path(root).rglob("*")]
    return frozenset(filter(None, listed))


def sections(skeleton):
    """Every section file the skeleton pulls in, in order, include blocks expanded."""
    skeleton = Path(skeleton)
    found = []
    for block in INCLUDE.finditer(skeleton.read_text()):
        for name in block.group(1).split():
            part = skeleton.parent / name
            found.append(part)
            if part.is_file():
                found += sections(part)
    return found


def source(skeleton):
    """The paper as pandoc sees it after include.lua: (front matter, text), each
    include block replaced by its files, their front matter joining the skeleton's."""
    skeleton = Path(skeleton)
    text = skeleton.read_text()
    front = FRONT.match(text)
    meta = (yaml.safe_load(front.group(1)) if front else None) or {}

    def expand(block):
        parts = []
        for name in block.group(1).split():
            if not (skeleton.parent / name).is_file():
                continue  # problems() reports it; pandoc would stop on it
            part_meta, part_text = source(skeleton.parent / name)
            for key, value in part_meta.items():
                meta.setdefault(key, value)
            parts.append(part_text)
        return "\n".join(parts)

    return meta, INCLUDE.sub(expand, text)


def images(skeleton):
    """Every image the paper shows, the teaser included, as written."""
    meta, text = source(skeleton)
    found = IMAGE.findall(text)
    if meta.get("teaser"):
        found.insert(0, str(meta["teaser"]))
    return found


def figure_names():
    from treasure_island.figures import FIGURES

    return set(FIGURES)


def problems(skeleton, root=ROOT, figures=None):
    """What stops the build: text left out, evidence missing, images unknown."""
    skeleton = Path(skeleton)
    listed = sections(skeleton)
    found = [f"{part}: listed but missing" for part in listed if not part.is_file()]
    results = skeleton.parent / "sections/results"
    for part in sorted(results.glob("*.md")) if results.is_dir() else []:
        if part not in listed:
            found.append(f"{part}: not listed in any section, so it's left out")
        found += _evidence_problems(part, root)
    if figures is None:
        figures = figure_names()
    for image in images(skeleton):
        if image.startswith("figures/"):
            if Path(image).stem not in figures:
                found.append(f"{image}: no named figure called {Path(image).stem!r}")
        elif image not in committed(Path(root)):
            found.append(f"{image}: not a committed file")
    return found


def _evidence_problems(part, root):
    head = "\n".join(part.read_text().splitlines()[:MARKER_LINES])
    markers = MARKER.findall(head)
    if not markers:
        hint = "<!-- experiment: name --> or <!-- result: name -->"
        return [f"{part}: no marker; name its evidence in the first lines, {hint}"]
    return [
        f"{part}: {kind} {name!r} isn't in the repository"
        for kind, name in markers
        if EVIDENCE[kind](name) not in committed(Path(root))
    ]


def warnings(skeleton, aux=None):
    """The sprint's limits, from the skeleton's front matter."""
    found = []
    meta, _ = source(skeleton)
    words = len(str(meta.get("abstract") or "").split())
    low, high = meta.get("abstract-words") or DEFAULT_ABSTRACT_WORDS
    if not low <= words <= high:
        found.append(f"abstract is {words} words; the sprint asks for {low}–{high}")
    cap = int(meta.get("max-pages") or DEFAULT_MAX_PAGES)
    if aux and Path(aux).exists():
        # paper.md sets \label{main-end} just before References, so the page
        # it lands on is the last page of main text.
        match = MAIN_END.search(Path(aux).read_text())
        if match and int(match.group(1)) > cap:
            found.append(f"{match.group(1)} pages before References; the cap is {cap}")
    return found


def main(argv):
    skeleton = argv[0] if argv else "paper/paper.md"
    aux = argv[1] if len(argv) > 1 else None
    errors = problems(skeleton)
    for line in errors:
        print(f"error: {line}")
    for line in warnings(skeleton, aux):
        print(f"warning: {line}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
