# Implements: tooling/one-command-each, tooling/locked-dependencies, ci/ci-minutes, ci/ci-runs-everything, assets/remade-by-one-command, assets/catwalk, treasure-island/reference-games, results/examples-folder, figures/named-figures, figures/figures-published, ci/examples-remade-in-ci, tuning/metrics-by-rule, tuning/teacher-rounds
.PHONY: install lint test spec-check assets catwalk reference-games examples examples-check figure figures tune tune-eval
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
examples-check:  # remake the examples; fail if anything but the manifests' times changed
	$(MAKE) examples
	python3 .github/scripts/examples_unchanged.py
figure:  # one named figure from a committed run: make figure NAME=silent-game
	uv run treasure-island figure $(NAME)
figures:  # every figure, into figures/
	uv run treasure-island figure --all
tune-eval:  # score configs/tuning.toml by rule, into runs/scratch/tuning/metrics.json
	uv run python -m treasure_island.tuning --eval-only
tune:  # Claude Code tunes the game, ROUNDS rounds on tuning/round-<n> branches; you pick
	uv run python -m treasure_island.tuning --rounds $(or $(ROUNDS),3)
