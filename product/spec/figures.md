# Figures

- **named-figures:** Every graphic in the report has a name, and `make figure NAME=<name>` builds it from committed runs with no keys and no network, so anyone can rebuild it after `git clone`.
- **two-lines:** Each figure comes with its two lines: the command that rebuilds it from the committed run, and the command that plays the game again into a new run folder, so a reader can check it for free or rerun it for real.
- **rerun-matches:** A figure's rerun command names a config that holds the same settings and seed as the committed run it was built from, so a rerun is the same game and not a lookalike.
- **figures-published:** CI builds every figure and publishes the set as an Actions artifact, never calling a model, so every pull request carries the current graphics.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `named-figures` | `src/treasure_island/figures.py`, `src/treasure_island/cli.py`, `Makefile` | `test_named_figures_build_offline_from_committed_runs`, `test_named_figures_every_figure_builds_and_an_unknown_name_fails` |
| `two-lines` | `src/treasure_island/figures.py` | `test_two_lines_sit_next_to_the_figure` |
| `rerun-matches` | `src/treasure_island/figures.py` | `test_rerun_matches_every_committed_run_without_spending`, `test_rerun_matches_catches_a_config_that_differs` |
| `figures-published` | `.github/workflows/blocking-checks.yml`, `Makefile`, `.gitignore` | `test_figures_published_as_an_artifact_by_the_gate` |
