# Viewer

- **one-renderer:** Every frame of a run, whether shown in the browser or baked into a GIF, is drawn by the same code from the event log, so the two can never show a different game.
- **frame-shows-the-swarm:** A frame shows the grid, every pirate on it, whose turn it is, what that pirate said in a speech bubble and the log lines it saw, so a reader grasps a turn at a glance without reading the events.
- **watch-live:** `treasure-island watch runs/<name>` opens a browser page that follows the run's event log as it's written, and steps through a finished run the same way, so a game is as much fun to watch as to read.
- **render-gif:** `treasure-island render runs/<name>` writes an animated GIF of the whole run, one frame per turn, so a game can be shared where no browser runs, such as a pull request.
- **art-folder:** The viewer draws pirates, tiles and the treasure from `assets/` and has no plain shape to fall back on, so a reader always sees the approved art, and missing art is an error rather than a different picture.
- **sprite-from-definition:** Each pirate's sprite comes from its definition in the run's config, or the default crew's when the run doesn't say, so the viewer shows the crew that was configured.
- **sprite-follows-action:** A pirate faces the way it last moved, walks on the turn it moves, and digs or cheers on the turn it digs, so a reader can see what it did from the animation.
- **crowds-fan-out:** Pirates sharing a square fan out so every label stays visible, even on the landing square in a corner: up to six keep their labels inside the square, so a neighbouring square can't cover them, and a bigger crowd spreads sideways.
- **slideshow-file:** `treasure-island slideshow runs/<name>` writes one HTML file holding every turn's frame and story line, which the left and right arrow keys step through, offline and with no server, so a reader can study a game at their own pace or pass it on as a file.
- **long-log-lines:** The log strip wraps a long line rather than cutting it off, and always shows the newest lines, so a reader never loses what a pirate wrote.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-renderer` | `src/treasure_island/viewer.py` | `test_one_renderer_the_gif_holds_exactly_the_frames_the_page_serves`, `test_one_renderer_rendering_twice_gives_an_identical_gif` |
| `frame-shows-the-swarm` | `src/treasure_island/viewer.py` | `test_frame_shows_the_swarm_every_pirate_whose_turn_the_bubble_and_the_log`, `test_crowds_fan_out_every_pirate_on_one_square_shows`, `test_frame_shows_the_swarm_as_an_image_with_grid_panel_and_log` |
| `watch-live` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_watch_live_the_page_follows_the_log_as_it_is_written`, `test_watch_live_the_command_names_its_address` |
| `render-gif` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_render_gif_writes_one_frame_per_turn_next_to_the_run`, `test_render_gif_writes_where_asked` |
| `art-folder` | `src/treasure_island/viewer.py`, `pyproject.toml` | `test_art_folder_every_empty_square_is_a_sand_tile_from_the_assets`, `test_art_folder_a_pirate_is_exactly_its_sprite_and_never_a_shape`, `test_art_folder_a_dug_square_and_a_found_treasure_use_their_art`, `test_art_folder_missing_art_is_an_error_not_a_different_picture`, `test_art_folder_the_art_loads_from_outside_the_repository` |
| `sprite-from-definition` | `src/treasure_island/viewer.py` | `test_sprite_from_definition_uses_the_configured_look`, `test_sprite_from_definition_a_run_that_does_not_say_gets_the_default_crew`, `test_sprite_from_definition_the_frame_draws_the_given_look` |
| `sprite-follows-action` | `src/treasure_island/viewer.py` | `test_sprite_follows_action_a_pirate_faces_the_way_it_moves`, `test_sprite_follows_action_it_keeps_facing_that_way_and_stands_still`, `test_sprite_follows_action_walking_alternates_its_feet`, `test_sprite_follows_action_each_pirate_alternates_its_own_feet`, `test_sprite_follows_action_digging_and_finding_the_treasure`, `test_sprite_follows_action_others_stay_as_they_were` |
| `crowds-fan-out` | `src/treasure_island/viewer.py` | `test_crowds_fan_out_every_pirate_on_one_square_shows`, `test_crowds_fan_out_up_to_six_labels_stay_inside_their_square`, `test_crowds_fan_out_a_big_crowd_never_stacks_and_stays_on_the_board`, `test_crowds_fan_out_a_pirate_leaving_the_crowd_covers_no_label`, `test_crowds_fan_out_a_lone_pirate_stands_on_its_square`, `test_crowds_fan_out_every_label_shows_on_the_landing_square` |
| `slideshow-file` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_slideshow_file_one_command_writes_it_next_to_the_run`, `test_slideshow_file_writes_where_asked`, `test_slideshow_file_holds_the_renderer_s_frame_for_every_turn`, `test_slideshow_file_holds_every_turn_s_story`, `test_slideshow_file_a_run_without_stories_still_steps`, `test_slideshow_file_the_arrow_keys_step_through_it`, `test_slideshow_file_needs_no_server_or_network`, `test_slideshow_file_writing_it_opens_no_socket`, `test_slideshow_file_a_pirate_s_words_cannot_break_out_of_the_page`, `test_slideshow_file_the_same_game_writes_the_same_bytes` |
| `long-log-lines` | not yet | — |
