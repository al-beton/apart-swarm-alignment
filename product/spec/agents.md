# Agents

- **one-interface:** Every agent, scripted or model, answers one request with reply text and its cost, and the game can't tell which kind answered, so a scripted agent can stand in for a model anywhere a model goes.
- **scripted-sees-the-prompt:** A scripted agent decides from the request a model would get, and from what it remembers of its own earlier requests, so nothing it does is beyond what a model could do.
- **grid-sweep:** The `scripted/sweep` agent digs where it stands and otherwise walks the grid row by row, turning back at the far corner, so it finds the treasure in bounded time and gives the visuals a game that ends.
- **counter:** The `scripted/counter` agent says the next number each turn and never digs, so a run has chatter to show and a game that plays to its turn limit.
- **free-runs-in-ci:** A full run with each scripted agent completes in CI without an API call or a key, so the whole path from config to events is proved at no cost.
- **committed-runs:** A run of each scripted agent is committed under `runs/`, passes the event-log validator and replays byte-identical, so the visuals have evidence to build from without rerunning anything.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-interface` | `src/treasure_island/backends.py`, `src/treasure_island/runs.py` | `test_one_interface_every_scripted_agent_answers_like_a_model`, `test_one_interface_each_run_gets_a_fresh_agent` |
| `scripted-sees-the-prompt` | `src/treasure_island/agents.py`, `src/treasure_island/game.py` | `test_scripted_sees_the_prompt_the_sweep_reads_where_it_is`, `test_scripted_sees_the_prompt_memory_is_per_pirate` |
| `grid-sweep` | `src/treasure_island/agents.py`, `configs/sweep.toml` | `test_grid_sweep_walks_row_by_row_and_turns_back_at_the_far_corner`, `test_grid_sweep_finds_the_treasure_from_anywhere` |
| `counter` | `src/treasure_island/agents.py`, `configs/counter.toml` | `test_counter_says_the_next_number_each_turn_and_never_digs` |
| `free-runs-in-ci` | `configs/sweep.toml`, `configs/counter.toml`, `.github/workflows/blocking-checks.yml` | `test_free_runs_in_ci_each_scripted_config_plays_a_full_game` |
| `committed-runs` | `runs/sweep-seed-5/**`, `runs/counter-seed-1/**` | `test_committed_runs_pass_the_validator_and_replay_byte_identical` |
