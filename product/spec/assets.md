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
- **treasure-shown:** The treasure has a closed chest, an open chest, and the question mark and X that mark its square.
- **viewer-parts:** The viewer has a speech bubble, a side panel, an arrow for whose turn it is, a portrait and a pixel font.
- **sheet-shows-everything:** `assets/sheet.png` shows all the art on one page, at game size and in play.
- **sheet-on-every-pr:** Every pull request shows one comment with a sheet of all the art from its latest commit, so nobody has to run anything to see it.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `plain-files` | `assets/README.md`, `assets/generate.py` | `test_plain_files_are_pngs_the_guide_names` |
| `remade-by-one-command` | `Makefile`, `assets/generate.py` | `test_remade_by_one_command_committed_images_match_the_code` |
| `original-art` | reviewer, `assets/pirates.py`, `assets/tiles.py`, `assets/treasure.py`, `assets/ui.py`, `assets/font.py`, `assets/pixels.py` | — |
| `game-size` | `assets/pixels.py` | `test_game_size_tiles_and_sprites_are_48px` |
| `any-pirate` | `assets/pirates.py` | `test_any_pirate_takes_any_personality_colour_and_label`, `test_any_pirate_refuses_a_label_that_will_not_fit` |
| `charming-personalities` | `assets/pirates.py` | `test_charming_personalities_are_twenty_and_all_different` |
| `label-on-hat` | `assets/pirates.py`, `src/treasure_island/looks.py` | `test_label_on_hat_is_dark_on_cream_whatever_the_colour`, `test_label_on_hat_stays_put_from_every_direction` |
| `four-directions` | `assets/pirates.py` | `test_four_directions_each_walk_with_three_frames` |
| `actions-shown` | `assets/pirates.py` | `test_actions_shown_digging_and_cheering_differ_from_standing` |
| `ground-tiles` | `assets/tiles.py` | `test_ground_tiles_are_opaque_and_look_different` |
| `treasure-shown` | `assets/treasure.py` | `test_treasure_shown_chests_and_marks_exist_and_differ` |
| `viewer-parts` | `assets/ui.py`, `assets/font.py`, `assets/pirates.py` | `test_viewer_parts_bubble_fits_its_text`, `test_viewer_parts_panel_stretches_to_any_size`, `test_viewer_parts_font_covers_printable_ascii`, `test_viewer_parts_portrait_is_the_head_enlarged` |
| `sheet-shows-everything` | `assets/generate.py` | `test_sheet_shows_everything_is_committed_and_wide_enough` |
| `sheet-on-every-pr` | `.github/workflows/asset-sheet.yml` | `test_sheet_on_every_pr_runs_on_pull_request_and_never_pull_request_target`, `test_sheet_on_every_pr_can_only_write_pull_requests`, `test_sheet_on_every_pr_runs_no_code_from_the_branch`, `test_sheet_on_every_pr_skips_forks_and_never_gates`, `test_sheet_on_every_pr_shows_the_latest_commit_s_sheet_in_one_comment` |
