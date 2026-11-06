# Implements: tooling/one-command-each, tooling/locked-dependencies, ci/ci-minutes, ci/ci-runs-everything
.PHONY: install lint test spec-check
install:
	uv sync --frozen
lint:
	uv run ruff check .
	uv run ruff format --check .
test:  # in parallel, one worker per core
	uv run pytest -n auto
spec-check:
	uv run python .github/scripts/spec_check.py
