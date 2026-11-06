# Implements: tooling/one-command-each, tooling/locked-dependencies, ci/ci-minutes, ci/ci-runs-everything, assets/remade-by-one-command, assets/catwalk, treasure-island/reference-games, results/examples-folder
.PHONY: install lint test spec-check assets catwalk reference-games examples
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
examples:  # play the example games again, GIFs included, into examples/
	uv run python -m treasure_island.examples
