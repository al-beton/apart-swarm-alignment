# Runs

- **run-command:** `treasure-island run CONFIG --seed N` plays one game into a new folder under `runs/`, and never overwrites an earlier run, so every result keeps its evidence.
- **run-folder:** A run folder holds `events.jsonl`, `replies.jsonl`, `config.json` and `manifest.json`, so it's all anyone needs to check or rebuild that run.
- **replies-keyed:** Every model reply is stored under a key made from everything that shaped the request (agent, model, prompt, temperature and seed), so a reply is only ever reused for the request that earned it.
- **manifest-varies:** `manifest.json` holds what varies between identical runs (times, cost and cache hits), so nothing else in the folder has to.
- **replay-byte-identical:** `treasure-island replay runs/<name>` plays the game again from the stored replies and fails unless its events are byte-identical to `events.jsonl`, with no keys and no network, so anyone can check a committed run for free.
- **no-silent-model-calls:** Replay never calls a model, and a reply it can't find fails the replay, so checking a run can never cost money.
- **walking-skeleton:** A tiny game (a grid, moving, digging, one treasure) stands in for the full rules, so the whole path from config to events can be proved before they're settled.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `run-command` | `src/treasure_island/cli.py`, `src/treasure_island/runs.py` | `test_run_command_makes_a_new_folder_each_time` |
| `run-folder` | `src/treasure_island/runs.py` | `test_run_folder_holds_events_replies_config_and_manifest`, `test_run_folder_events_pass_the_validator` |
| `replies-keyed` | `src/treasure_island/runs.py` | `test_replies_keyed_each_part_of_the_request_changes_the_key`, `test_replies_keyed_a_repeated_request_reuses_its_reply` |
| `manifest-varies` | `src/treasure_island/runs.py` | `test_manifest_varies_holds_times_cost_and_cache_hits`, `test_manifest_varies_two_identical_runs_differ_nowhere_else` |
| `replay-byte-identical` | `src/treasure_island/cli.py`, `src/treasure_island/runs.py` | `test_replay_byte_identical_with_no_keys_or_network`, `test_replay_byte_identical_fails_when_a_reply_changed`, `test_replay_byte_identical_leaves_the_folder_untouched` |
| `no-silent-model-calls` | `src/treasure_island/runs.py` | `test_no_silent_model_calls_a_missing_reply_fails_the_replay` |
| `walking-skeleton` | `src/treasure_island/game.py`, `src/treasure_island/backends.py`, `configs/skeleton.toml` | `test_walking_skeleton_digging_on_the_treasure_ends_the_game`, `test_walking_skeleton_a_pirate_stays_on_the_grid`, `test_walking_skeleton_a_reply_it_cannot_read_is_a_turn_with_no_action`, `test_walking_skeleton_the_game_stops_at_the_turn_limit`, `test_walking_skeleton_an_unknown_model_is_refused` |
