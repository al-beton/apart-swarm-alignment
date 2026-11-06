# Results

- **examples-folder:** `examples/` holds at least three committed games that look different, each a run folder plus its GIF, so there's a fixed set to look at after every change and something for a new reader to open straight away.
- **examples-listed:** `examples/README.md` says in one line what each game shows, so a reader can pick one.
- **examples-small:** Each example's GIF is under 2 MB, so a clone stays small and the GIF opens at once.
- **examples-stay-true:** CI replays every example and fails if its logs or its GIF differ, and says which command remakes them, so an example always shows what the code does today.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `examples-folder` | `src/treasure_island/examples.py`, `Makefile`, `examples/**`, `configs/small-crew.toml` | `test_examples_folder_holds_at_least_three_different_games`, `test_examples_folder_each_holds_what_the_game_wrote_and_a_gif` |
| `examples-listed` | `examples/README.md` | `test_examples_listed_each_in_one_line_of_the_guide` |
| `examples-small` | `src/treasure_island/examples.py` | `test_examples_small_each_gif_is_under_2_mb` |
| `examples-stay-true` | `src/treasure_island/examples.py`, `src/treasure_island/saved_game.py` | `test_examples_stay_true_every_log_replays_byte_identical`, `test_examples_stay_true_every_gif_matches_what_is_drawn_now`, `test_examples_stay_true_a_stale_example_says_how_to_remake_it` |
