# Results

- **examples-folder:** `examples/` holds at least three committed games that look different, each a run folder plus its GIF, so there's a fixed set to look at after every change and something for a new reader to open straight away.
- **examples-listed:** `examples/README.md` says in one line what each game shows, so a reader can pick one.
- **examples-small:** Each example's GIF is under 2 MB, so a clone stays small and the GIF opens at once.
- **examples-stay-true:** CI replays every example and fails if its logs or its GIF differ, and says which command remakes them, so an example always shows what the code does today.
- **examples-on-every-pr:** Every pull request's one game comment shows each example's GIF inline, with its name and how it ended, from that pull request's latest commit, so a change to the games can be seen without running anything.
- **result-folder:** Each result is `results/<name>/`, holding its run folders and a short `README.md` that says the question, what was run, what it shows and what it cost, so a finding can be kept and shared with its evidence beside it.
- **results-are-runs:** A result's run folders use the same format as `runs/` and `examples/`, so the same commands work on them.
- **results-listed:** `results/README.md` lists every result, so a reader can see at once what's been found.
- **results-stay-checkable:** CI replays every committed result with no keys and no network, so anyone can trust a result without paying to rerun it.
- **sample-result:** `results/` holds a small sample result from a scripted game, so the layout can be copied and costs nothing to check.
- **result-gif:** Each result holds a `game.gif` of one of its games, under 2 MB, so a reader sees it play without running anything.
- **result-on-its-pr:** A pull request that adds or changes a result shows what it found, how each game ended and its GIF in the one game comment, from committed files alone, and one that touches no result shows no results section, so a reviewer can see what came in without running anything.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `examples-folder` | `src/treasure_island/examples.py`, `Makefile`, `examples/**`, `configs/small-crew.toml` | `test_examples_folder_holds_at_least_three_different_games`, `test_examples_folder_each_holds_what_the_game_wrote_and_a_gif` |
| `examples-listed` | `examples/README.md` | `test_examples_listed_each_in_one_line_of_the_guide` |
| `examples-small` | `src/treasure_island/examples.py` | `test_examples_small_each_gif_is_under_2_mb` |
| `examples-stay-true` | `src/treasure_island/examples.py`, `src/treasure_island/saved_game.py` | `test_examples_stay_true_every_log_replays_byte_identical`, `test_examples_stay_true_every_gif_matches_what_is_drawn_now`, `test_examples_stay_true_a_stale_example_says_how_to_remake_it` |
| `examples-on-every-pr` | `.github/workflows/game-gif.yml` | `test_examples_on_every_pr_shows_each_gif_inline_with_its_ending`, `test_examples_on_every_pr_reads_the_commit_without_running_its_code`, `test_examples_on_every_pr_lists_examples_from_that_commit` |
| `result-folder` | `results/**` | `test_result_folder_each_holds_run_folders_and_says_what_it_found` |
| `results-are-runs` | `results/**` | `test_results_are_runs_with_the_same_files`, `test_results_are_runs_the_same_commands_work` |
| `results-listed` | `results/README.md` | `test_results_listed_in_the_index_exactly_once_each` |
| `results-stay-checkable` | `results/**`, `.github/workflows/blocking-checks.yml` | `test_results_stay_checkable_replaying_with_no_keys_or_network` |
| `sample-result` | `results/sample-sweep-seeds/**` | `test_sample_result_is_a_scripted_game_that_cost_nothing` |
| `result-gif` | `results/**`, `results/README.md` | `test_result_gif_each_result_has_one_under_2_mb` |
| `result-on-its-pr` | `.github/workflows/game-gif.yml` | `test_result_on_its_pr_shows_summary_endings_and_gif`, `test_result_on_its_pr_reads_only_what_the_pull_request_changed`, `test_result_on_its_pr_has_no_section_without_a_result`, `test_result_on_its_pr_finds_the_section_a_result_calls_what_it_shows` |
