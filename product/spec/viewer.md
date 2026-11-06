# Viewer

- **one-renderer:** Every frame of a run, whether shown in the browser or baked into a GIF, is drawn by the same code from the event log, so the two can never show a different game.
- **frame-shows-the-swarm:** A frame shows the grid, every pirate on it, whose turn it is, what that pirate said in a speech bubble and the log lines it saw, so a reader grasps a turn at a glance without reading the events.
- **watch-live:** `treasure-island watch runs/<name>` opens a browser page that follows the run's event log as it's written, and steps through a finished run the same way, so a game is as much fun to watch as to read.
- **render-gif:** `treasure-island render runs/<name>` writes an animated GIF of the whole run, one frame per turn, so a game can be shared where no browser runs, such as a pull request.
- **art-folder:** The game's art lives in `assets/`, and the viewer draws plain tiles and pirates until there's art for them, so the viewer works before the art is settled.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-renderer` | not yet | — |
| `frame-shows-the-swarm` | not yet | — |
| `watch-live` | not yet | — |
| `render-gif` | not yet | — |
| `art-folder` | not yet | — |
