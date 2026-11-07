# CI

- **one-gate:** A single required check gates every merge.
- **checks-on-every-pr:** Every pull request is checked, whatever branch it's based on, so stacked pull requests get the same checks as ones into main.
- **checks-over-prose:** Anything that can be checked automatically ends up checked by CI rather than left to the reviewer.
- **simple-code:** Code stays simple enough that the linter never calls it too complex.
- **ci-runs-everything:** CI runs the linter, every test and the spec check before anything merges.
- **ci-minutes:** The gate is quick: every check that gates a merge is a step of the one `blocking-checks` job, the tests run in parallel (one worker per core) and dependencies are cached between runs. A newer run for the same pull request cancels the one in progress, unless it is a draft run that would only be skipped, and draft pull requests are not checked until they are marked ready.
- **no-model-calls:** CI never calls a model, and no API keys are stored as secrets.
- **examples-remade-in-ci:** CI runs `make examples-check`, which remakes the examples and fails if that changes anything in `examples/` but the times in their manifests, so a change to what a saved game holds remakes the examples in the same pull request.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-gate` | `.github/workflows/blocking-checks.yml` | — |
| `checks-on-every-pr` | `.github/workflows/blocking-checks.yml` | — |
| `checks-over-prose` | `.agents/skills/review-pr/SKILL.md` | — |
| `simple-code` | `pyproject.toml` | — |
| `ci-runs-everything` | `.github/workflows/blocking-checks.yml`, `Makefile` | `test_ci_minutes_the_gate_runs_every_check` |
| `ci-minutes` | `.github/workflows/blocking-checks.yml`, `Makefile`, `pyproject.toml`, `uv.lock`, `.agents/skills/open-pr/SKILL.md`, `.agents/skills/deliver-issue/SKILL.md` | `test_ci_minutes_the_gate_is_one_job`, `test_ci_minutes_tests_run_in_parallel_with_cached_dependencies`, `test_ci_minutes_the_gate_runs_every_check`, `test_ci_minutes_newer_runs_cancel_older_ones_and_drafts_wait` |
| `no-model-calls` | `.github/workflows/blocking-checks.yml` | `test_no_model_calls_no_secret_but_the_github_token` |
| `examples-remade-in-ci` | `.github/workflows/blocking-checks.yml`, `Makefile`, `.github/scripts/examples_unchanged.py` | `test_examples_remade_in_ci_the_gate_runs_the_check`, `test_examples_remade_in_ci_only_the_manifests_times_may_change`, `test_examples_remade_in_ci_any_other_change_fails_and_says_how_to_fix_it` |
