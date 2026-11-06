<!-- Implements: tooling/one-command-each, tooling/how-we-work -->
# Treasure Island

> **History reset on 6 November 2026.** `main` was restarted from a fresh first commit to make clones small. If your clone is older than that, don't push from it: it would bring the old history back. Clone again. Nothing was lost: the old history is in `al-beton/something-to-lose-apart-ai-collusion`. Edu: your Treasure Island draft is still on `experiment/treasure-island`, with the same content and you as author, now on top of the new `main`. Your original commit is backed up in the old repo as `edu/treasure-island-original`. To bring over anything you hadn't pushed, copy the files or make a patch from your old clone, then apply it on a branch from the new `main`.

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
| `uv run treasure-island run configs/skeleton.toml --seed 0` | plays one game into a new folder under `runs/` |
| `uv run treasure-island replay runs/<name>` | checks a run offline, for free, by rebuilding its events from its stored replies |

## How we work

A team of coding agents builds this, directed by one person. Coding agents start at `AGENTS.md`.

1. Work starts as a GitHub issue with checkbox acceptance criteria.
2. Spec first: the statements in `product/spec/`, `experiments/spec/` or `contributing/spec/` change before anything else.
3. Then a failing test, then the smallest code that passes it, then the trace: each file names the statements it implements, and each statement the files and tests behind it.
4. One draft pull request per issue; CI must be green.
5. Codex reviews it, then a reviewer agent that didn't write it; every thread is answered and resolved before merging.

## License

[MIT](LICENSE).
