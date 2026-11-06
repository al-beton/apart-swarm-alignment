# Viewer

- **one-renderer:** Every frame of a run, whether shown in the browser or baked into a GIF, is drawn by the same code from the event log, so the two can never show a different game.
- **frame-shows-the-swarm:** A frame shows the grid, every pirate on it, whose turn it is, what that pirate said in a speech bubble and the log lines it saw, so a reader grasps a turn at a glance without reading the events.
- **watch-live:** `treasure-island watch runs/<name>` opens a browser page that follows the run's event log as it's written, and steps through a finished run the same way, so a game is as much fun to watch as to read.
- **render-gif:** `treasure-island render runs/<name>` writes an animated GIF of the whole run, one frame per turn, so a game can be shared where no browser runs, such as a pull request.
- **art-folder:** The viewer draws pirates, tiles and the treasure from `assets/` and has no plain shape to fall back on, so a reader always sees the approved art, and missing art is an error rather than a different picture.
- **sprite-from-definition:** Each pirate's sprite comes from its definition in the run's config, or the default crew's when the run doesn't say, so the viewer shows the crew that was configured.
- **sprite-follows-action:** A pirate faces the way it last moved, walks on the turn it moves, and digs or cheers on the turn it digs, so a reader can see what it did from the animation.
- **crowds-fan-out:** Pirates sharing a square fan out inside the board, so every one and its label stay visible, even on the landing square in a corner.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-renderer` | `src/treasure_island/viewer.py` | `test_one_renderer_the_gif_holds_exactly_the_frames_the_page_serves` |
| `frame-shows-the-swarm` | `src/treasure_island/viewer.py` | `test_frame_shows_the_swarm_every_pirate_whose_turn_the_bubble_and_the_log`, `test_frame_shows_the_swarm_pirates_on_one_square_are_all_visible`, `test_frame_shows_the_swarm_as_an_image_with_grid_panel_and_log` |
| `watch-live` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_watch_live_the_page_follows_the_log_as_it_is_written`, `test_watch_live_the_command_names_its_address` |
| `render-gif` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_render_gif_writes_one_frame_per_turn_next_to_the_run`, `test_render_gif_writes_where_asked` |
| `art-folder` | not yet | — |
| `sprite-from-definition` | not yet | — |
| `sprite-follows-action` | not yet | — |
| `crowds-fan-out` | not yet | — |
