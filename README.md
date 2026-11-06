<!-- Implements: tooling/one-command-each, tooling/how-we-work -->
# Treasure Island

A reproducible sandbox for asking when a swarm of LLM agents whistleblows, and what in their environment changes that. It's our entry to Apart's multi-agent oversight and control track.

The game itself is still to be built; what it should do goes in `product/spec/`.

## Commands

| Command | What it does |
|---|---|
| `make install` | installs the locked dependencies with [uv](https://docs.astral.sh/uv/) |
| `make lint` | runs the ruff lint and format checks |
| `make test` | runs every test, in parallel |
| `make spec-check` | checks that the spec, the code and the tests point at each other |
| `uv run treasure-island --help` | shows what the game's command can do |

## How we work

A team of coding agents builds this, directed by one person. Coding agents start at `AGENTS.md`.

1. Work starts as a GitHub issue with checkbox acceptance criteria.
2. Spec first: the statements in `product/spec/`, `experiments/spec/` or `contributing/spec/` change before anything else.
3. Then a failing test, then the smallest code that passes it, then the trace: each file names the statements it implements, and each statement the files and tests behind it.
4. One draft pull request per issue; CI must be green.
5. Codex reviews it, then a reviewer agent that didn't write it; every thread is answered and resolved before merging.

## License

[MIT](LICENSE).
