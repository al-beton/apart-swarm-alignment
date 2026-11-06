# Runs

- **run-command:** `treasure-island run CONFIG --seed N` plays one game into a new folder under `runs/`, and never overwrites an earlier run, so every result keeps its evidence.
- **run-folder:** A run folder holds `events.jsonl`, `replies.jsonl`, `config.json` and `manifest.json`, so it's all anyone needs to check or rebuild that run.
- **replies-keyed:** Every model reply is stored under a key made from everything that shaped the request (agent, model, prompt, temperature and seed), so a reply is only ever reused for the request that earned it.
- **manifest-varies:** `manifest.json` holds what varies between identical runs (times, cost and cache hits), so nothing else in the folder has to.
- **replay-byte-identical:** `treasure-island replay runs/<name>` plays the game again from the stored replies and fails unless its events are byte-identical to `events.jsonl`, with no keys and no network, so anyone can check a committed run for free.
- **no-silent-model-calls:** Replay never calls a model, and a reply it can't find fails the replay, so checking a run can never cost money.
- **plays-live:** `treasure-island run` opens the live view by default, and `--no-watch` turns it off for CI, so you always watch a game play, whether it's new or cached.
- **paced-from-cache:** While it's being watched, a run plays turn by turn at a watchable pace even when every reply comes from the cache, so a cached game never jumps to the end.
- **cache-across-runs:** A run reuses an earlier run's reply to the same request and keeps a copy in its own folder, so a repeat spends nothing and its folder alone can regenerate it; an agent that remembers things its request doesn't show always answers for itself, since no other run's reply can be trusted for it.
- **no-cache:** `--no-cache` ignores earlier runs' replies, asks for them again and writes a new run folder, so a game can be regenerated.
- **walking-skeleton:** A tiny game (a grid, moving, digging, saying a line, one treasure) stands in for the full rules, so the whole path from config to events can be proved before they're settled.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `run-command` | `src/treasure_island/cli.py`, `src/treasure_island/runs.py` | `test_run_command_makes_a_new_folder_each_time` |
| `run-folder` | `src/treasure_island/runs.py` | `test_run_folder_holds_events_replies_config_and_manifest`, `test_run_folder_events_pass_the_validator` |
| `replies-keyed` | `src/treasure_island/runs.py` | `test_replies_keyed_each_part_of_the_request_changes_the_key`, `test_replies_keyed_a_repeated_request_reuses_its_reply`, `test_replies_keyed_a_stored_reply_survives_any_line_separator` |
| `manifest-varies` | `src/treasure_island/runs.py` | `test_manifest_varies_holds_times_cost_and_cache_hits`, `test_manifest_varies_two_identical_runs_differ_nowhere_else` |
| `replay-byte-identical` | `src/treasure_island/cli.py`, `src/treasure_island/runs.py` | `test_replay_byte_identical_with_no_keys_or_network`, `test_replay_byte_identical_fails_when_a_reply_changed`, `test_replay_byte_identical_leaves_the_folder_untouched` |
| `no-silent-model-calls` | `src/treasure_island/runs.py` | `test_no_silent_model_calls_a_missing_reply_fails_the_replay` |
| `plays-live` | `src/treasure_island/cli.py` | `test_plays_live_run_opens_the_view_by_default`, `test_plays_live_no_watch_opens_nothing_and_never_waits`, `test_plays_live_stays_open_at_a_terminal_but_not_in_a_script` |
| `paced-from-cache` | `src/treasure_island/runs.py` | `test_paced_from_cache_a_new_game_plays_turn_by_turn`, `test_paced_from_cache_a_cached_game_plays_turn_by_turn_too` |
| `cache-across-runs` | `src/treasure_island/runs.py`, `src/treasure_island/agents.py` | `test_cache_across_runs_a_longer_game_keeps_a_scripted_agent_s_memory`, `test_cache_across_runs_a_repeat_asks_the_model_nothing`, `test_cache_across_runs_its_folder_alone_regenerates_the_game`, `test_cache_across_runs_only_the_same_request_reuses_a_reply`, `test_cache_across_runs_replay_never_borrows_from_another_run` |
| `no-cache` | `src/treasure_island/cli.py`, `src/treasure_island/runs.py` | `test_no_cache_asks_again_into_a_new_folder`, `test_no_cache_a_later_repeat_reuses_the_newest_replies` |
| `walking-skeleton` | `src/treasure_island/game.py`, `src/treasure_island/agents.py`, `configs/skeleton.toml` | `test_walking_skeleton_digging_on_the_treasure_ends_the_game`, `test_walking_skeleton_a_pirate_stays_on_the_grid`, `test_walking_skeleton_a_reply_it_cannot_read_is_a_turn_with_no_action`, `test_walking_skeleton_the_game_stops_at_the_turn_limit`, `test_walking_skeleton_an_unknown_model_is_refused`, `test_walking_skeleton_a_said_line_is_recorded` |
