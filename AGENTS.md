<!-- Implements: agent-setup/entry-point, agent-setup/reuse-old-work, review/spec-first, safety/no-secrets, workflow/al-only, workflow/prototype-pace, workflow/audience, workflow/one-routine, research/results-have-a-place -->
# Treasure Island: agent guide

Treasure Island is a reproducible sandbox for asking when a swarm of LLM agents whistleblows, and what in their environment changes that. It's our entry to Apart's multi-agent oversight and control track.

## Where things are

- **Spec (intent, read first):** `product/spec/` (the game), `experiments/spec/` (what we're finding out with it) and `contributing/spec/` (how we build it). One file per area. Each ends with "Where this is enforced", which says which files enforce each statement and which tests prove it.
- **Code:** `src/treasure_island/`, tests in `tests/`, CI in `.github/`. Every file names the statements it implements on an `Implements:` line (files that can't hold comments, such as JSON, lockfiles and symlinks, are traced by their table row). Docs are the comments and docstrings next to the code.
- **How to do each step:** the skills in `.agents/skills/` (also linked as `.claude/skills/`): `deliver-issue` (the whole routine, issue to merged), and the steps it chains: `build-issue`, `write-spec-change`, `trace-spec`, `open-pr`, `review-pr`, `address-review`, `merge-pr`. Who does what (manager, delivery lead, builders, reviewers, Codex, researcher) and the queue labels are in `team`.
- **Paper:** `paper/`, one Markdown file per section, each results section bound to the experiment or result it reports; `paper/README.md` explains the loop and `paper/plan.md` holds what the paper says. Built with `make paper-html` or `make paper-pdf`, previewed on GitHub Pages from every pull request.
- **Games:** `results/` keeps findings, each with the games behind it; `examples/` is the fixed set of games remade with the code; `runs/` is everyday evidence. `results/README.md` says how to add one.
- **Work** is tracked as GitHub issues on this repository.

Al handles accounts, API keys and spending. Agents never put keys in code, configs, logs or commits.

## Who it's for

First, the people working in this code over and over to make it really good; next, researchers reviewing or extending it; then judges of the paper. So a change should make repeated use easier: quick to run, easy to see, easy to compare.

## Pace

This is a hackathon prototype. Submissions close Monday 9 November 2026. Aim for the smallest change that works and can be shared. Fix real bugs; decline speculative hardening and edge cases nobody has hit, with a reason. A pull request gets one Codex round: fix P1 findings in one push, answer the rest "follow-up", and the builder merges it once checks are green and Codex has finished on the latest commit.

## Commands

```sh
make install      # uv dependencies
make lint         # ruff lint and format check
make test         # every test
make spec-check   # spec ↔ code ↔ tests traceability (fails CI if broken)
```

## The loop

Every issue goes **spec → failing test → code → trace → draft PR → review → merge**, one small commit at a time (`deliver-issue`).

## Code review rules

Follow the `review-pr` skill. In short:
1. **Start with the spec.** Is each new or changed statement in `product/spec/`, `experiments/spec/` or `contributing/spec/` good? A behaviour change with no spec change is a finding.
2. **Then the code:** does it do what the statements say, reasonably? Its `Implements:` lines and the spec's "Where this is enforced" table must agree.
3. **Then the tests listed for each changed statement.**
4. **Never:** pull request or issue numbers in code, specs or tests; secrets anywhere.

Put each finding inline on the lines it concerns.

## Reusing the old work

Our earlier project stays public at [`al-beton/something-to-lose-apart-ai-collusion`, commit `24961e54c`](https://github.com/al-beton/something-to-lose-apart-ai-collusion/tree/24961e54c). Nothing from it is here, so copy what a change needs from that commit. The modules are under `src/collusion_lab/`:

- `backends.py`: model endpoints
- `cache.py`: replaying from cached responses
- `runner.py`, `manifest.py`, `provenance.py`: running games and recording what produced them
- `estimate.py`: cost estimates before a run
- `debrief.py`: asking agents about the game afterwards
- `leisure.py`, `conditions/free_time.py`: the Sudoku time
- `report/`: HTML reports
- `deploy/` (at the top of that repository): serving models on Modal
