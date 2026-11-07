# Assets

- **plain-files:** All game art is plain PNG files in `assets/` that any renderer can load, with a guide listing their names and sizes.
- **remade-by-one-command:** `make assets` remakes every image from code, and the committed images always match what the code draws.
- **original-art:** All the art is original and drawn in code; none is copied from another game.
- **game-size:** Squares and sprites are 48px, so a 10x10 board is 480px at real size.
- **any-pirate:** A pirate is made from three things: one of 20 personalities, any RGB colour and a label.
- **charming-personalities:** Personalities differ charmingly but not distractingly: skin, hair, beard, eye patch, earring and grin, with the same hat and coat.
- **label-on-hat:** A label of up to two letters or digits sits in a cream blob on the hat, dark on cream whatever the colour, and stays in the same place from every direction.
- **four-directions:** Pirates face four directions, each with a standing frame and two walking frames.
- **actions-shown:** Pirates also have digging and cheering poses.
- **ground-tiles:** The ground tiles are sand and grass, dug sand that still looks walkable, water that doesn't, and sinking sand.
- **treasure-shown:** The treasure's square has a question mark to mark it for the reader, until it is dug up and becomes the cave.
- **treasure-cave:** Once the treasure is dug up its square is a cave the pirates go into, with gold glinting in its mouth over two frames, and room beside the door for a stack of hats.
- **hat-stack:** Each pirate that goes into the cave leaves a small copy of its hat by the door, in its colour with its label, stacked in the order they went in with the first at the bottom; a crew of six fits on the square with every label showing, and a bigger crew squeezes up to stay on it.
- **going-in:** A pirate going into the cave is drawn from behind, sinking into its mouth over four steps, so a single frame still reads as going in.
- **viewer-parts:** The viewer has a scroll note with a quill for a pirate writing, an open scroll for a pirate reading, a side panel, an arrow for whose turn it is, a portrait and a pixel font.
- **sheet-shows-everything:** `assets/sheet.png` shows all the art on one page, at game size and in play.
- **catwalk:** `make catwalk` writes `assets/catwalk.gif`, in which every pirate walks in all four directions across a sample of the walkable ground, in under 2 MB, so the style and the movement can be judged at a glance.
- **sheet-on-every-pr:** Every pull request shows one comment with a sheet of all the art and the catwalk beside it, both from its latest commit, so nobody has to run anything to see them.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `plain-files` | `assets/README.md`, `assets/generate.py` | `test_plain_files_are_pngs_the_guide_names` |
| `remade-by-one-command` | `Makefile`, `assets/generate.py`, `assets/catwalk.py` | `test_remade_by_one_command_committed_images_match_the_code`, `test_catwalk_is_deterministic_and_the_committed_gif_matches_the_code` |
| `original-art` | reviewer, `assets/cave.py`, `assets/pirates.py`, `assets/tiles.py`, `assets/treasure.py`, `assets/ui.py`, `assets/font.py`, `assets/pixels.py` | — |
| `game-size` | `assets/pixels.py` | `test_game_size_tiles_and_sprites_are_48px` |
| `any-pirate` | `assets/pirates.py` | `test_any_pirate_takes_any_personality_colour_and_label`, `test_any_pirate_refuses_a_label_that_will_not_fit` |
| `charming-personalities` | `assets/pirates.py` | `test_charming_personalities_are_twenty_and_all_different` |
| `label-on-hat` | `assets/pirates.py`, `src/treasure_island/looks.py` | `test_label_on_hat_is_dark_on_cream_whatever_the_colour`, `test_label_on_hat_stays_put_from_every_direction` |
| `four-directions` | `assets/pirates.py` | `test_four_directions_each_walk_with_three_frames` |
| `actions-shown` | `assets/pirates.py` | `test_actions_shown_digging_and_cheering_differ_from_standing` |
| `ground-tiles` | `assets/tiles.py` | `test_ground_tiles_are_opaque_and_look_different` |
| `treasure-shown` | `assets/treasure.py` | `test_treasure_shown_a_question_mark_marks_it_until_it_is_dug_up` |
| `treasure-cave` | `assets/cave.py`, `assets/generate.py` | `test_treasure_cave_is_a_square_that_glints_and_leaves_room_for_the_hats` |
| `hat-stack` | `assets/cave.py` | `test_hat_stack_is_empty_with_nobody_inside`, `test_hat_stack_puts_the_first_in_at_the_bottom`, `test_hat_stack_shows_every_label_for_a_crew_of_six`, `test_hat_stack_keeps_a_big_crew_on_the_square`, `test_hat_stack_hats_are_small_and_carry_the_label` |
| `going-in` | `assets/cave.py` | `test_going_in_sinks_into_the_mouth_step_by_step` |
| `viewer-parts` | `assets/ui.py`, `assets/font.py`, `assets/pirates.py` | `test_viewer_parts_scroll_note_fits_its_text`, `test_viewer_parts_scroll_note_carries_the_quill`, `test_viewer_parts_open_scroll_is_small_and_holds_no_words`, `test_viewer_parts_panel_stretches_to_any_size`, `test_viewer_parts_font_covers_printable_ascii`, `test_viewer_parts_portrait_is_the_head_enlarged` |
| `sheet-shows-everything` | `assets/generate.py` | `test_sheet_shows_everything_is_committed_and_wide_enough` |
| `catwalk` | `assets/catwalk.py`, `Makefile`, `assets/README.md` | `test_catwalk_every_pirate_walks_in_all_four_directions`, `test_catwalk_pirates_keep_to_their_own_patch_of_ground`, `test_catwalk_crosses_a_sample_of_walkable_tiles`, `test_catwalk_gif_shows_exactly_what_was_drawn`, `test_catwalk_is_deterministic_and_the_committed_gif_matches_the_code`, `test_catwalk_is_under_two_megabytes`, `test_catwalk_make_catwalk_and_make_assets_both_write_it` |
| `sheet-on-every-pr` | `.github/workflows/asset-sheet.yml` | `test_sheet_on_every_pr_runs_on_pull_request_and_never_pull_request_target`, `test_sheet_on_every_pr_can_only_write_pull_requests`, `test_sheet_on_every_pr_runs_no_code_from_the_branch`, `test_sheet_on_every_pr_skips_forks_and_never_gates`, `test_sheet_on_every_pr_shows_the_latest_commit_s_sheet_in_one_comment`, `test_sheet_on_every_pr_shows_the_catwalk_beside_the_sheet_from_the_same_commit` |
