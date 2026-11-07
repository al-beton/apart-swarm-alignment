# Agents

- **backend-interface:** A model backend answers one request with reply text and its cost, so any model can be plugged in without the game knowing which.
- **no-model-yet:** Every model no backend serves is refused, so nothing can spend money by accident.
- **openrouter-backend:** A model named `openrouter/<model id>` plays through OpenRouter's chat completions with the four tools: its tool call comes back in the one reply form, and its cost is the reply's own usage figure, totalled in the run's manifest. A reply that gives no cost stops the run, since the spending cap couldn't count it. Default, Al to confirm: the model may answer without a tool, which counts as a bad reply, and thinking off sends no reasoning setting.
- **key-from-the-environment:** A backend's key comes only from its environment variable, which `.env.example` names with no value, and a missing key stops a run before the game starts, saying which variable to set.
- **model-per-pirate:** A pirate's config may name a model, and that pirate plays through the LLM brain while the rest of the crew plays the config's brain, so one crew can mix models and scripts.
- **one-request-per-turn:** Each LLM turn is one request holding only the system prompt, the turn's text and the pirate's tools as tool definitions, so requests stay small and every model is asked the same thing.
- **reply-is-a-tool-call:** A backend answers with JSON text naming one tool and its arguments, and the reasoning when thinking is on, so any provider's tool call reaches the game in one form.
- **ask-once-more:** A reply that isn't a valid tool call is recorded and counts as a failed action: the pirate is told why and asked again, and after `failed_tries` refusals in one turn (default 2) its turn passes with no action.
- **reply-cap:** Each reply, its thought and its tool call together, is capped at a small output size, `reply_tokens` in the config (default 300); a model's own built-in reasoning has its own budget (`model-reasoning`).
- **plays-then-replays:** A whole game plays through a fake backend, then replays byte-identical from the replies its folder stored, with no backend at all, so an LLM game costs money once and is free to check ever after.
- **free-runs-in-ci:** A full game with each scripted brain completes in CI without an API call or a key, so the whole path from config to logs is proved at no cost.
- **committed-runs:** A game of each scripted brain is committed under `runs/`, passes the event-log validator and replays byte-identical, so the visuals have evidence to build from without rerunning anything.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `backend-interface` | `src/treasure_island/backends.py`, `src/treasure_island/runs.py` | `test_backend_interface_a_backend_gives_reply_text_and_its_cost` |
| `no-model-yet` | `src/treasure_island/backends.py` | `test_no_model_yet_every_model_is_refused` |
| `openrouter-backend` | `src/treasure_island/openrouter.py`, `src/treasure_island/backends.py`, `tests/openrouter-reply.json` | `test_openrouter_backend_a_tool_call_comes_back_in_the_one_reply_form`, `test_openrouter_backend_asks_with_the_four_tools_and_the_key`, `test_openrouter_backend_a_reply_with_no_tool_call_is_passed_on_to_be_refused`, `test_openrouter_backend_the_manifest_totals_the_reply_s_cost`, `test_openrouter_backend_a_reply_with_no_cost_stops_the_run` |
| `key-from-the-environment` | `src/treasure_island/backends.py`, `src/treasure_island/saved_game.py`, `.env.example` | `test_key_from_the_environment_a_missing_key_stops_the_run_before_the_game`, `test_key_from_the_environment_env_example_names_the_key_with_no_value` |
| `model-per-pirate` | `src/treasure_island/config.py`, `src/treasure_island/strategies.py` | `test_model_per_pirate_a_pirate_with_a_model_gets_the_llm_brain`, `test_model_per_pirate_the_model_is_saved_with_the_config`, `test_model_per_pirate_a_model_must_be_text` |
| `one-request-per-turn` | not yet | — |
| `reply-is-a-tool-call` | `src/treasure_island/llm.py` | `test_reply_is_a_tool_call_becomes_the_action` |
| `ask-once-more` | not yet | — |
| `reply-cap` | `src/treasure_island/config.py`, `src/treasure_island/llm.py` | `test_reply_cap_defaults_to_300_tokens_and_a_config_can_set_it` |
| `plays-then-replays` | `src/treasure_island/llm.py`, `src/treasure_island/saved_game.py` | `test_plays_then_replays_a_whole_game_through_a_fake_backend`, `test_plays_then_replays_with_no_backend_a_missing_reply_spends_nothing` |
| `free-runs-in-ci` | `configs/s-sweep.toml`, `configs/say-a-number.toml`, `.github/workflows/blocking-checks.yml` | `test_free_runs_in_ci_each_scripted_brain_plays_a_full_game` |
| `committed-runs` | `runs/s-sweep-seed-7/**`, `runs/reference-s-sweep/**`, `runs/reference-say-a-number/**` | `test_committed_runs_pass_the_validator_and_replay_byte_identical` |
