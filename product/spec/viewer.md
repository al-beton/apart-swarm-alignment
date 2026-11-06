# Viewer

- **one-renderer:** Every frame of a run, whether shown in the browser or baked into a GIF, is drawn by the same code from the event log, so the two can never show a different game.
- **frame-shows-the-swarm:** A frame shows the grid, every pirate on it, whose turn it is, what that pirate said in a speech bubble and the log lines it saw, so a reader grasps a turn at a glance without reading the events.
- **watch-live:** `treasure-island watch runs/<name>` opens a browser page that follows the run's event log as it's written, and steps through a finished run the same way, so a game is as much fun to watch as to read.
- **render-gif:** `treasure-island render runs/<name>` writes an animated GIF of the whole run, one frame per turn, so a game can be shared where no browser runs, such as a pull request.
- **art-folder:** The viewer takes any tile it finds in `assets/` and draws plain tiles and pirates for the rest, so it works before the art is settled and picks the art up as it lands.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-renderer` | `src/treasure_island/viewer.py` | `test_one_renderer_the_gif_holds_exactly_the_frames_the_page_serves` |
| `frame-shows-the-swarm` | `src/treasure_island/viewer.py` | `test_frame_shows_the_swarm_every_pirate_whose_turn_the_bubble_and_the_log`, `test_frame_shows_the_swarm_pirates_on_one_square_are_all_visible`, `test_frame_shows_the_swarm_as_an_image_with_grid_panel_and_log` |
| `watch-live` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_watch_live_the_page_follows_the_log_as_it_is_written`, `test_watch_live_the_command_names_its_address` |
| `render-gif` | `src/treasure_island/cli.py`, `src/treasure_island/viewer.py` | `test_render_gif_writes_one_frame_per_turn_next_to_the_run`, `test_render_gif_writes_where_asked` |
| `art-folder` | `src/treasure_island/viewer.py` | `test_art_folder_the_viewer_draws_without_art`, `test_art_folder_art_is_drawn_when_it_exists` |
