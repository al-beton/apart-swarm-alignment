<!-- Implements: paper/one-source, paper/numbers-from-logs, paper/games-replay, specs-and-docs/folder-guides, paper/forms-link-each-other, paper/teaser-moves-in-html -->
# Paper

The paper, written once in Markdown and built two ways: HTML to read and share while we write, and the PDF we submit. It's made to be iterated quickly: every section is its own file, every results section is tied to the games behind it, and every push to a pull request publishes a preview.

## How it fits together

- **The text** is in `sections/`, one file per section: `abstract.md` (as front matter), `introduction.md`, `related-work.md`, `methods.md`, `results.md`, `discussion.md`, `conclusion.md`, then `endmatter.md` (the LLM usage statement, code and data) and `appendix.md` after the references. These are what you edit.
- **The order** is the list in `paper.md`. To move a section, move its line; to add one, write the file and list it; to leave one out, remove its line. `paper.md` also holds the title page's fields and the sprint's limits.
- **The results** are one file per experiment under `sections/results/`, listed in `sections/results.md` in the order they appear. Each file's first lines carry a marker, `<!-- experiment: name -->` for an experiment spec in `experiments/spec/` or `<!-- result: name -->` for a result folder in `results/`. `check.py` fails the build when that evidence isn't in the repository, when a results file isn't listed, or when an image isn't a named figure (`figures/<name>.gif`, from `src/treasure_island/figures.py`) or a committed file. So a results section can only report games anyone can replay. It also replays every game behind each results section, by its recorded actions under today's rules: each run folder in the result its marker names and each one its numbers read. No model is called, so it's free and takes seconds, and a game that no longer plays the same way stops the build, naming the game and the first turn that differs. The build adds each named figure's two lines under it, the command that rebuilds it and the one that plays the game again, taken from the registry (`lines.py`), so don't type them in the caption.
- **The plan** is `plan.md`: the question, the claim and which evidence each results section rests on. Agree it there first.
- **The look:** `apart.html` and `style.css` for the HTML, `apart.latex` for the PDF, both in Apart's layout. `include.lua` pulls the sections into the skeleton. `stills.py` copies the images into the build and makes a PNG still of each GIF for the PDF. `teaser.py` makes the title page's teaser, `paper/figures/teaser.png`, from two turns of a committed game: `make paper-teaser`, or `make paper-teaser TEASER_RUN=… LEAK_TURN=… PASS_TURN=…` for another game.
- **The references:** `references.bib`, cited as `[@key]`.

## Build

```sh
make paper-html    # paper/build/paper.html
make paper-pdf     # paper/build/paper.pdf, by way of paper/build/paper.tex
make paper-watch   # rebuilds on every save; preview at http://127.0.0.1:8765/preview.html
make paper-check   # just the contract: sections listed, evidence committed, figures named, numbers from the logs, games replay
```

You need `pandoc` for the HTML, `tectonic` for the PDF and `fswatch` with `pdftoppm` for the watch loop (`brew install pandoc tectonic fswatch poppler`). Output goes to `paper/build/`, which isn't committed. The build warns when the abstract is outside the sprint's word range or the main text runs past its page cap; both limits are `abstract-words` and `max-pages` in `paper.md`.

## Preview on every pull request

A pull request that touches `paper/` gets one comment linking its HTML and PDF on GitHub Pages, under `pr-<number>/`, rebuilt on every push (`.github/workflows/paper-preview.yml`). The site's front page is `main`'s build: <https://al-beton.github.io/apart-swarm-alignment/>.

## Writing a results section

1. Run the experiment and commit its games as a result (`results/README.md` says how) or write its spec in `experiments/spec/`.
2. Write `sections/results/<name>.md`: the marker, one `##` heading, the text, and figures from the registry. Take every number from the games' own logs, and follow it with a comment saying where: `115<!-- from results/<name>/*/events.jsonl: mean(game_over(game)['score'] for game in data) -->`. The glob names `events.jsonl` or `manifest.json` files under `results/`; the expression is Python over `data`, those files in path order (an events file is its list of records, a manifest its dict), with `mean`, `percent` and `game_over` (a game's last record's `game_over`) beside `len`, `sum`, `min`, `max` and `round`. A count is `len(data)` or a `sum(1 for ...)`, a mean is `mean(...)`, a percentage is `percent(part, whole)` with the `%` after the number. `make paper-check` recomputes each one and fails on a number that doesn't match, rounded to the decimals it's written with, and on a number with no comment. Write names and commands, like `seed 7`, in backticks; a name such as pirate-1 isn't taken for a number.
3. Add its line to `sections/results.md` and its row to `plan.md`.
4. Open a pull request. The preview comment shows the paper with the section in place.

## The two forms link each other

The HTML and the PDF are one paper. `web-url` and `pdf-url` in `paper.md`'s front matter are where the paper workflow publishes `main` on GitHub Pages. The PDF's title-page footnote links the HTML, where every game is playable. The HTML's first line under the title links the PDF. `make paper-pdf` fails if either is empty.

## A moving teaser

The teaser (Figure 1) can be a named figure's GIF. In `paper.md`'s front matter:

```yaml
teaser: figures/dig-debug-game.gif   # the HTML shows it animating
teaser-still: paper/figures/teaser.png   # the PDF shows this in its place
```

`make paper-images` builds the GIF from its committed run, like any named figure. A PDF can't animate, so it shows `teaser-still`. Leave that out and the PDF shows the GIF's last frame, the game as it ended. Links in the caption are underlined in the HTML and coloured in the PDF.
