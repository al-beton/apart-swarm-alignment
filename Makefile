# Implements: tooling/one-command-each, tooling/locked-dependencies, ci/ci-minutes, ci/ci-runs-everything, assets/remade-by-one-command, assets/catwalk, treasure-island/reference-games, results/examples-folder, figures/named-figures, figures/figures-published, ci/examples-remade-in-ci, runs/replay-checks, paper/built-two-ways, paper/figures-carry-their-lines
.PHONY: install lint test spec-check assets catwalk reference-games examples examples-check figure figures replay-all paper-tools paper-check paper-images paper-html paper-tex paper-pdf paper-watch
install:
	uv sync --frozen
lint:
	uv run ruff check .
	uv run ruff format --check .
test:  # in parallel, one worker per core
	uv run pytest -n auto
spec-check:
	uv run python .github/scripts/spec_check.py
assets:  # redraw every image in assets/
	uv run python -m assets.generate
catwalk:  # write the GIF of every pirate walking
	uv run python -m assets.catwalk
reference-games:  # replay the scripted pirates' committed games into runs/
	uv run python -m treasure_island.strategies
replay-all:  # replay every committed game by its recorded actions, outside the checks
	uv run python -m treasure_island.replay
examples:  # play the example games again, GIFs included, into examples/
	uv run python -m treasure_island.examples
examples-check:  # remake the examples; fail if anything but the manifests' times changed
	$(MAKE) examples
	python3 .github/scripts/examples_unchanged.py
figure:  # one named figure from a committed run: make figure NAME=silent-game
	uv run treasure-island figure $(NAME)
figures:  # every figure, into figures/
	uv run treasure-island figure --all

# The paper: write paper/sections/*.md (paper/paper.md lists them in order), build to paper/build/ (gitignored).
PAPER_BUILD ?= paper/build
PANDOC = pandoc paper/paper.md --from markdown --lua-filter paper/include.lua --resource-path=.:paper --metadata-file=$(PAPER_BUILD)/figure-lines.json --number-sections --toc --toc-depth=1
paper-tools:
	@command -v pandoc >/dev/null || { echo "pandoc is missing: brew install pandoc (or see pandoc.org/installing)"; exit 1; }
paper-check:  # the paper's contract with the repository: every section listed, every results section's evidence committed, every figure named
	uv run python -m paper.check paper/paper.md
paper-images: paper-check  # every image the paper shows, into the build: named figures rebuilt from committed runs, plus a PNG still of each GIF for the PDF
	uv run treasure-island figure --all
	@mkdir -p $(PAPER_BUILD)
	uv run python -m paper.stills paper/paper.md $(PAPER_BUILD)
	uv run python -m paper.lines paper/paper.md $(PAPER_BUILD)
paper-html: paper-tools paper-images  # fast, for writing: open paper/build/paper.html
	@cp paper/style.css $(PAPER_BUILD)/
	$(PANDOC) --standalone --template paper/apart.html --css style.css --math-method=mathml --citeproc -o $(PAPER_BUILD)/paper.html
paper-tex: paper-tools paper-images  # the .tex, with references.bib and the images beside it, ready for Overleaf
	@cp paper/references.bib $(PAPER_BUILD)/
	$(PANDOC) --template paper/apart.latex --natbib -o $(PAPER_BUILD)/paper.tex
paper-pdf: paper-tex
	@command -v tectonic >/dev/null || { echo "tectonic is missing: brew install tectonic (or see tectonic-typesetting.github.io)"; exit 1; }
	cd $(PAPER_BUILD) && tectonic --keep-logs --keep-intermediates paper.tex
	@uv run python -m paper.check paper/paper.md $(PAPER_BUILD)/paper.aux
paper-watch:  # the writing loop: on every save, HTML then .tex then PDF; preview at http://127.0.0.1:8765/preview.html
	@PAPER_BUILD=$(PAPER_BUILD) paper/watch.sh
