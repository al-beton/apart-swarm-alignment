# Implements: paper/one-source, paper/built-two-ways, paper/sections-bind-to-evidence, paper/sprint-rules-checked, paper/numbers-from-logs, paper/preview-on-every-pr, paper/paper-plan, paper/figures-carry-their-lines
"""The paper is one Markdown source whose results sections can only report
committed evidence, built two ways and previewed on every pull request."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from PIL import Image

from paper import check, lines, stills
from treasure_island import figures

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


def with_results(tmp_path, text):
    """The fake repository's results section saying `text`, with two games
    and a manifest under results/known/ to take its numbers from."""
    skeleton = fake_repo(tmp_path)
    for seed, score, dug in ((1, 0, False), (2, 230, True)):
        game = tmp_path / f"results/known/seed-{seed}"
        game.mkdir()
        end = {"game_over": {"score": score, "treasure_dug_up": dug}}
        (game / "events.jsonl").write_text('{"turn": 0}\n' + json.dumps(end) + "\n")
        (game / "manifest.json").write_text(json.dumps({"cost_usd": seed * 0.25}))
    part = tmp_path / "paper/sections/results/one.md"
    part.write_text(part.read_text() + "\n" + text + "\n")
    return skeleton


GAMES = "results/known/*/events.jsonl"


def test_numbers_from_logs_a_number_that_matches_its_logs_passes(tmp_path):
    skeleton = with_results(
        tmp_path,
        f"The crew scored 230<!-- from {GAMES}: data[1][-1]['game_over']['score'] -->.",
    )
    assert problems(skeleton) == []


def test_numbers_from_logs_a_mismatch_fails_naming_the_section_and_number(tmp_path):
    skeleton = with_results(
        tmp_path,
        f"The crew scored 250<!-- from {GAMES}: data[1][-1]['game_over']['score'] -->.",
    )
    found = problems(skeleton)
    assert len(found) == 1
    assert "one.md" in found[0] and "250" in found[0] and "230" in found[0]


def test_numbers_from_logs_a_number_with_no_source_fails(tmp_path):
    skeleton = with_results(tmp_path, "The crew scored 230 in the second game.")
    found = problems(skeleton)
    assert len(found) == 1
    assert "one.md" in found[0] and "230" in found[0] and "no source" in found[0]


def test_numbers_from_logs_a_count_a_mean_and_a_percentage(tmp_path):
    dug = "sum(1 for game in data if game_over(game)['treasure_dug_up'])"
    text = (
        f"In 1<!-- from {GAMES}: {dug} --> of 2<!-- from {GAMES}: len(data) --> games"
        f" (50%<!-- from {GAMES}: percent({dug}, len(data)) -->) the treasure was dug up,"
        f" and the crew scored 115.0<!-- from {GAMES}: mean(game_over(game)['score'] for game in data) -->"
        " on average."
    )
    assert problems(with_results(tmp_path, text)) == []


def test_numbers_from_logs_reads_a_manifest_too(tmp_path):
    costs = "results/known/*/manifest.json"
    text = (
        f"The games cost $0.75<!-- from {costs}: sum(m['cost_usd'] for m in data) -->."
    )
    assert problems(with_results(tmp_path, text)) == []


def test_numbers_from_logs_a_source_outside_results_fails(tmp_path):
    outside = with_results(tmp_path, "It was 2<!-- from paper/paper.md: len(data) -->.")
    assert any("results/" in p for p in problems(outside))


def test_numbers_from_logs_a_source_matching_nothing_fails(tmp_path):
    none = with_results(
        tmp_path, "It was 2<!-- from results/known/*/nothing.jsonl: len(data) -->."
    )
    assert any("matches no committed file" in p for p in problems(none))


def test_numbers_from_logs_names_and_code_are_not_numbers(tmp_path):
    text = "pirate-1 dug at A5; `seed 7` replays it, as `runs/silent-seed-7` shows."
    assert problems(with_results(tmp_path, text)) == []


def test_numbers_from_logs_the_sample_section_reports_a_real_number():
    # Every real results section reports sourced numbers that recompute.
    sections = sorted((ROOT / "paper/sections/results").glob("*.md"))
    assert sections
    for section in sections:
        assert check.SOURCED.search(section.read_text()), section
        assert check.number_problems(section, ROOT) == [], section


def test_numbers_from_logs_a_negative_number_with_no_source_fails(tmp_path):
    for text in ("The difference was -115 points.", "(-115 points)", "-115 points."):
        found = problems(with_results(tmp_path / str(len(text)), text))
        assert len(found) == 1, text
        assert "-115 has no source" in found[0]


def test_numbers_from_logs_a_negative_number_with_a_source_is_compared(tmp_path):
    lower = "min(-game_over(game)['score'] for game in data)"  # -230
    right = with_results(
        tmp_path / "right", f"It moved by -230<!-- from {GAMES}: {lower} -->."
    )
    assert problems(right) == []
    wrong = with_results(
        tmp_path / "wrong", f"It moved by -115<!-- from {GAMES}: {lower} -->."
    )
    found = problems(wrong)
    assert len(found) == 1 and "says -115" in found[0] and "-230" in found[0]
    # A hyphen inside a name is still not a sign, nor a number.
    assert (
        problems(with_results(tmp_path / "names", "pirate-1 and seed-7 went in.")) == []
    )


def test_figures_carry_their_lines_each_shown_figure_s_lines_come_from_the_registry(
    tmp_path,
):
    # A skeleton that shows a registry figure, since the paper may show none.
    skeleton = fake_repo(tmp_path / "repo", image="figures/silent-game.gif")
    written = lines.write_lines(skeleton, tmp_path / "build")
    shown = {
        Path(image).stem
        for image in check.images(skeleton)
        if image.startswith("figures/")
    }
    found = json.loads(written.read_text())["figure_lines"]
    assert set(found) == shown == {"silent-game"}
    for name in shown:
        assert found[name] == [f"`{line}`" for line in lines.paper_lines(name)]


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc isn't installed")
def test_figures_carry_their_lines_the_built_html_holds_both_lines_under_each_figure(
    tmp_path,
):
    build = tmp_path / "build"
    subprocess.run(
        ["make", "-s", "paper-html", f"PAPER_BUILD={build}"], cwd=ROOT, check=True
    )
    html = (build / "paper.html").read_text()
    for image in check.images(SKELETON):
        if not image.startswith("figures/"):
            continue
        rebuild, rerun = lines.paper_lines(Path(image).stem)
        caption = re.search(
            rf'<img src="{re.escape(image)}".*?</figcaption>', html, re.DOTALL
        )
        assert caption, image
        assert f"<code>{rebuild}</code>" in caption.group(0)
        assert f"<code>{rerun}</code>" in caption.group(0)
    # Written once, by the build: no section copies a figure's lines by hand.
    for section in (ROOT / "paper/sections").rglob("*.md"):
        for name in figures.FIGURES:
            for line in lines.paper_lines(name):
                assert line not in section.read_text(), (section, line)


GAME = ROOT / "results/sample-sweep-seeds/small-crew-seed-1"


def with_game(tmp_path, result="known", changed=False, text=""):
    """The fake repository with a real committed game in results/<result>/,
    its first turn's outcome moved when `changed`, and `text` in the section."""
    skeleton = fake_repo(tmp_path)
    game = tmp_path / f"results/{result}/game-1"
    shutil.copytree(GAME, game)
    if changed:
        events = (game / "events.jsonl").read_text().splitlines()
        first = json.loads(events[0])
        first["outcome"]["position"] = [9, 9]
        (game / "events.jsonl").write_text("\n".join([json.dumps(first), *events[1:]]))
    (tmp_path / f"results/{result}/README.md").write_text("# A result\n")
    part = tmp_path / "paper/sections/results/one.md"
    part.write_text(part.read_text() + "\n" + text + "\n")
    git(tmp_path, "add", "-A")
    check.committed.cache_clear()
    return skeleton


def test_games_replay_a_game_behind_a_section_that_replays_passes(tmp_path):
    assert problems(with_game(tmp_path)) == []


def test_games_replay_a_changed_game_fails_naming_it_and_the_turn(tmp_path):
    (found,) = problems(with_game(tmp_path, changed=True))
    assert "results/known/game-1" in found and "turn 0" in found
    assert "one.md" in found


def test_games_replay_a_game_a_number_reads_in_another_result_is_replayed_too(
    tmp_path,
):
    games = "results/other/*/events.jsonl"
    text = f"It took 1<!-- from {games}: len(data) --> game."
    (found,) = problems(with_game(tmp_path, result="other", changed=True, text=text))
    assert "results/other/game-1" in found and "turn 0" in found


def test_games_playable_the_teaser_game_s_page_is_its_log_rendered():
    from treasure_island import examples, viewer

    game = ROOT / "runs/natural-leak/dig-debug-seed-0"
    page = (game / "game.html").read_text(encoding="utf-8")
    assert examples.same_page(viewer.slideshow_page(game), page)


def test_games_playable_one_command_renders_any_game_folder():
    make = (ROOT / "Makefile").read_text()
    assert "game-page:" in make
    assert "treasure-island slideshow $(GAME) --out $(GAME)/game.html" in make
    assert "GAME ?= runs/natural-leak/dig-debug-seed-0" in make
    assert "`make game-page`" in (ROOT / "README.md").read_text()


def test_games_playable_the_teaser_caption_links_its_game_page():
    meta = yaml.safe_load(SKELETON.read_text().split("---")[1])
    url = "https://al-beton.github.io/apart-swarm-alignment/games/runs/natural-leak/dig-debug-seed-0/"
    assert f"]({url})" in meta["teaser-caption"]
    page = url.split("/games/", 1)[1].rstrip("/") + "/game.html"
    assert (ROOT / page).is_file()


def test_forms_link_each_other_the_skeleton_names_both_urls():
    meta, _ = check.source(SKELETON)
    pages = "https://al-beton.github.io/apart-swarm-alignment/main/"
    assert meta["web-url"] == pages + "paper.html"
    assert meta["pdf-url"] == pages + "paper.pdf"


def test_forms_link_each_other_each_template_names_the_other_form_first():
    latex = (ROOT / "paper/apart.latex").read_text()
    said = "This is the PDF version of this work. See the HTML version, with every game watchable, \\href{$web-url$}{here}."
    assert said in latex and latex.index(said) < latex.index(
        "$abstract$"
    )  # in the title block, above the abstract
    html = (ROOT / "paper/apart.html").read_text()
    title = html.index('<div class="titleblock">')
    first = html.index(
        "This is the HTML version of this work. See the PDF version <a", title
    )
    assert (
        html.index('<div class="authors">')
        < first
        < html.index('<section class="abstract">')
    )
    assert '<a href="$pdf-url$">here</a>' in html


def test_forms_link_each_other_the_pdf_build_fails_without_them(tmp_path):
    skeleton = tmp_path / "paper.md"
    skeleton.write_text("---\ntitle: T\nweb-url: ''\n---\n")
    found = check.submission_problems(skeleton)
    assert any("web-url" in line for line in found)
    assert any("pdf-url" in line for line in found)
    assert check.submission_problems(SKELETON) == []


def test_teaser_moves_in_html_the_dig_debug_game_is_a_named_figure():
    figure = figures.FIGURES["dig-debug-game"]
    assert figure.run == "runs/natural-leak/dig-debug-seed-0"
    assert figures.rerun_mismatch("dig-debug-game") is None


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="needs pandoc")
def test_teaser_moves_in_html_the_pdf_shows_the_still(tmp_path):
    skeleton = tmp_path / "paper.md"
    front = "---\ntitle: T\nteaser: figures/dig-debug-game.gif\n"
    for still, want in (
        ("teaser-still: paper/figures/teaser.png\n", "paper/figures/teaser.png"),
        ("", "figures/dig-debug-game.png"),
    ):
        skeleton.write_text(front + still + "---\nText.\n")

        def built(to):
            done = subprocess.run(
                [
                    "pandoc",
                    str(skeleton),
                    "--lua-filter",
                    str(ROOT / "paper/include.lua"),
                    "-s",
                    "-t",
                    to,
                    "--template",
                    str(ROOT / f"paper/apart.{'latex' if to == 'latex' else 'html'}"),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return done.stdout

        assert want in built("latex")
        assert "figures/dig-debug-game.gif" in built("html")
    skeleton.write_text(front + "teaser-still: paper/figures/teaser.png\n---\n")
    assert check.images(skeleton)[:2] == [
        "figures/dig-debug-game.gif",
        "paper/figures/teaser.png",
    ]


def test_teaser_moves_in_html_links_look_like_links():
    css = (ROOT / "paper/style.css").read_text()
    assert re.search(r"(?m)^a \{[^}]*text-decoration: underline", css)
    assert "colorlinks=true" in (ROOT / "paper/apart.latex").read_text()
    skeleton_images = check.images.__doc__ or ""
    assert "teaser-still" in skeleton_images
