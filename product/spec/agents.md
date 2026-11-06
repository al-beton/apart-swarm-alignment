# Agents

- **backend-interface:** A model backend answers one request with reply text and its cost, so any model can be plugged in without the game knowing which.
- **no-model-yet:** Every model is refused until a backend is added on purpose, so nothing can spend money by accident.
- **free-runs-in-ci:** A full game with each scripted brain completes in CI without an API call or a key, so the whole path from config to logs is proved at no cost.
- **committed-runs:** A game of each scripted brain is committed under `runs/`, passes the event-log validator and replays byte-identical, so the visuals have evidence to build from without rerunning anything.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `backend-interface` | `src/treasure_island/backends.py`, `src/treasure_island/runs.py` | `test_backend_interface_a_backend_gives_reply_text_and_its_cost` |
| `no-model-yet` | `src/treasure_island/backends.py` | `test_no_model_yet_every_model_is_refused` |
| `free-runs-in-ci` | `configs/s-sweep.toml`, `configs/say-a-number.toml`, `.github/workflows/blocking-checks.yml` | `test_free_runs_in_ci_each_scripted_brain_plays_a_full_game` |
| `committed-runs` | `runs/s-sweep-seed-7/**`, `runs/reference-s-sweep/**`, `runs/reference-say-a-number/**` | `test_committed_runs_pass_the_validator_and_replay_byte_identical` |
