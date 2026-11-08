# Implements: paper/one-source, paper/built-two-ways, paper/sections-bind-to-evidence, paper/sprint-rules-checked, paper/preview-on-every-pr, paper/paper-plan
"""The paper is one Markdown source whose results sections can only report
committed evidence, built two ways and previewed on every pull request."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from PIL import Image

from paper import check, stills

ROOT = Path(__file__).resolve().parents[1]
SKELETON = ROOT / "paper/paper.md"
WORKFLOW = ROOT / ".github/workflows/paper-preview.yml"

ABSTRACT = "---\nabstract: |\n  Lorem ipsum dolor sit amet consectetur.\n---\n"


def fake_repo(tmp_path, *, marker="<!-- result: known -->", image="figures/fig.gif"):
    """A tiny git repository with one known experiment, one known result, one
    committed image and a paper whose results section carries `marker` and
    shows `image`, all tracked; return the skeleton's path."""
    (tmp_path / "experiments/spec").mkdir(parents=True)
    (tmp_path / "experiments/spec/known.md").write_text("# Known\n")
    (tmp_path / "results/known").mkdir(parents=True)
    (tmp_path / "results/known/README.md").write_text("# Known\n")
    (tmp_path / "results/known/game.gif").write_bytes(b"GIF89a")
    paper = tmp_path / "paper/sections/results"
    paper.mkdir(parents=True)
    (tmp_path / "paper/paper.md").write_text(
        "---\ntitle: T\nabstract-words: [3, 9]\nmax-pages: 4\n---\n"
        "```{.include}\nsections/abstract.md\nsections/intro.md\nsections/results.md\n```\n"
    )
    (tmp_path / "paper/sections/abstract.md").write_text(ABSTRACT)
    (tmp_path / "paper/sections/intro.md").write_text("# Introduction\n\nText.\n")
    (tmp_path / "paper/sections/results.md").write_text(
        "# Results\n\n```{.include}\nresults/one.md\n```\n"
    )
    (paper / "one.md").write_text(
        f"<!-- Implements: paper/one-source -->\n{marker}\n\n## One\n\n![a]({image})\n"
    )
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "-A")
    check.committed.cache_clear()
    return tmp_path / "paper/paper.md"


def git(root, *arguments):
    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)


def problems(skeleton):
    return check.problems(skeleton, root=skeleton.parents[1], figures={"fig"})


def test_one_source_every_listed_section_exists_and_every_section_is_listed():
    listed = check.sections(SKELETON)
    assert listed, "the skeleton lists no sections"
    assert all(part.is_file() for part in listed)
    for part in (ROOT / "paper/sections/results").glob("*.md"):
        assert part in listed, f"{part.name} is written but not listed"
    # Every section file is pulled in somewhere, so no text is left behind.
    for part in (ROOT / "paper/sections").glob("*.md"):
        assert part in listed, f"{part.name} is written but not listed"


def test_one_source_a_missing_section_is_an_error(tmp_path):
    skeleton = fake_repo(tmp_path)
    (tmp_path / "paper/sections/intro.md").unlink()
    assert any("intro.md: listed but missing" in p for p in problems(skeleton))


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc isn't installed")
def test_one_source_builds_the_html_from_the_sections(tmp_path):
    build = tmp_path / "build"
    subprocess.run(
        ["make", "-s", "paper-html", f"PAPER_BUILD={build}"], cwd=ROOT, check=True
    )
    html = (build / "paper.html").read_text()
    for heading in ("Introduction", "Methods", "Results", "Conclusion"):
        assert heading in html
    # The results section's image sits beside the page, as the text names it.
    for image in check.images(SKELETON):
        assert (build / image).is_file(), image


def test_built_two_ways_make_knows_every_paper_target():
    for target in (
        "paper-check",
        "paper-html",
        "paper-tex",
        "paper-pdf",
        "paper-watch",
    ):
        dry = subprocess.run(
            ["make", "-n", target],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert dry.returncode == 0, f"{target}: {dry.stderr}"
    assert "paper/build/" in (ROOT / ".gitignore").read_text()


def test_built_two_ways_a_gif_becomes_a_still_for_the_pdf(tmp_path, monkeypatch):
    skeleton = fake_repo(tmp_path, image="results/known/game.gif")
    frames = [Image.new("RGB", (4, 4), colour) for colour in ("red", "blue")]
    frames[0].save(
        tmp_path / "results/known/game.gif", save_all=True, append_images=frames[1:]
    )
    monkeypatch.chdir(tmp_path)
    written = stills.write_stills(skeleton, tmp_path / "build")
    assert (tmp_path / "build/results/known/game.gif").is_file()
    still = tmp_path / "build/results/known/game.png"
    assert still in written
    with Image.open(still) as image:  # the last frame: the game as it ended
        assert image.getpixel((0, 0)) == (0, 0, 255)


def test_sections_bind_to_evidence_an_unknown_experiment_fails(tmp_path):
    skeleton = fake_repo(tmp_path, marker="<!-- experiment: unknown -->")
    assert [
        "experiment 'unknown' isn't in the repository" in p for p in problems(skeleton)
    ] == [True]


def test_sections_bind_to_evidence_an_unknown_result_fails(tmp_path):
    skeleton = fake_repo(tmp_path, marker="<!-- result: unknown -->")
    assert [
        "result 'unknown' isn't in the repository" in p for p in problems(skeleton)
    ] == [True]


def test_sections_bind_to_evidence_a_results_section_without_a_marker_fails(tmp_path):
    skeleton = fake_repo(tmp_path, marker="<!-- no evidence named -->")
    (found,) = problems(skeleton)
    assert "no marker" in found and "<!-- experiment: name -->" in found
    # And an unlisted results file is caught too: it would silently be left out.
    (tmp_path / "paper/sections/results/two.md").write_text(
        "<!-- result: known -->\n## Two\n"
    )
    assert any("two.md: not listed" in p for p in problems(skeleton))


def test_sections_bind_to_evidence_an_unregistered_figure_fails(tmp_path):
    skeleton = fake_repo(tmp_path, image="figures/nope.gif")
    assert problems(skeleton) == ["figures/nope.gif: no named figure called 'nope'"]
    skeleton = fake_repo(tmp_path / "again", image="results/known/missing.png")
    assert problems(skeleton) == ["results/known/missing.png: not a committed file"]


def test_sections_bind_to_evidence_an_untracked_file_is_not_committed(tmp_path):
    # It exists on this disk and nowhere else: a clean clone wouldn't have it.
    skeleton = fake_repo(tmp_path, image="results/known/local.png")
    (tmp_path / "results/known/local.png").write_bytes(b"PNG")
    check.committed.cache_clear()
    assert problems(skeleton) == ["results/known/local.png: not a committed file"]
    # The same for a result folder or an experiment spec that isn't tracked.
    (tmp_path / "results/local").mkdir()
    (tmp_path / "results/local/README.md").write_text("# Local\n")
    (tmp_path / "paper/sections/results/one.md").write_text(
        "<!-- result: local -->\n## One\n"
    )
    check.committed.cache_clear()
    assert [
        "result 'local' isn't in the repository" in p for p in problems(skeleton)
    ] == [True]


def test_sections_bind_to_evidence_the_paper_passes(tmp_path):
    # The real paper: every marker names committed evidence, every image is a
    # named figure or a committed file, and a known experiment marker works too.
    assert check.problems(SKELETON) == []
    assert problems(fake_repo(tmp_path, marker="<!-- experiment: known -->")) == []
    assert problems(fake_repo(tmp_path / "b", image="results/known/game.gif")) == []


def test_sprint_rules_checked_abstract_length_is_a_warning(tmp_path):
    skeleton = fake_repo(tmp_path)
    assert check.warnings(skeleton) == []
    (tmp_path / "paper/sections/abstract.md").write_text(
        "---\nabstract: Two words.\n---\n"
    )
    assert check.warnings(skeleton) == ["abstract is 2 words; the sprint asks for 3–9"]
    assert problems(skeleton) == [], "a limit is a warning, never an error"
    # The limits come from the skeleton's front matter, so the real paper's are there.
    meta, _ = check.source(SKELETON)
    assert meta["abstract-words"] and meta["max-pages"]


def test_sprint_rules_checked_page_cap_read_from_the_aux(tmp_path):
    skeleton = fake_repo(tmp_path)
    aux = tmp_path / "paper.aux"
    aux.write_text("\\newlabel{main-end}{{}{6}{References}{section*.1}{}}\n")
    assert check.warnings(skeleton, aux) == ["6 pages before References; the cap is 4"]
    aux.write_text("\\newlabel{main-end}{{}{4}{References}{section*.1}{}}\n")
    assert check.warnings(skeleton, aux) == []


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def test_preview_on_every_pr_publishes_to_a_slot_and_one_comment():
    on = workflow()[True]  # yaml reads `on` as True
    assert "paper/**" in on["pull_request"]["paths"]
    assert "main" in on["push"]["branches"]
    job = workflow()["jobs"]["paper-preview"]
    assert "pr-{0}" in job["env"]["SLOT"] and "'main'" in job["env"]["SLOT"]
    runs = " ".join(str(step.get("run", "")) for step in job["steps"])
    assert "make paper-html paper-pdf" in runs
    assert "gh-pages" in runs and "url=main/paper.html" in runs
    assert runs.count("<!-- paper-preview -->") >= 2, "the marker finds its own comment"
    assert "PATCH" in runs, "an existing comment is edited, not added to"


def test_preview_on_every_pr_is_not_the_gate_and_holds_no_key():
    text = WORKFLOW.read_text()
    assert "blocking-checks" not in workflow()["jobs"]
    secrets = set(re.findall(r"secrets\.(\w+)", text))
    assert secrets <= {"GITHUB_TOKEN"}, secrets
    assert "github.token" in text
    assert not re.search(r"(?i)(openrouter|adaption|anthropic|openai)_api_key", text)


def test_paper_plan_names_each_results_section():
    plan = (ROOT / "paper/plan.md").read_text()
    for part in (ROOT / "paper/sections/results").glob("*.md"):
        assert f"`{part.name}`" in plan, f"plan.md has no row for {part.name}"
    for heading in (
        "## The question",
        "## The claim",
        "## What each results section rests on",
    ):
        assert heading in plan
