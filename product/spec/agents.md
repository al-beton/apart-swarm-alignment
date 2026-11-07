# Agents

- **backend-interface:** A model backend answers one request with reply text and its cost, so any model can be plugged in without the game knowing which.
- **no-model-yet:** Every model is refused until a backend is added on purpose, so nothing can spend money by accident.
- **model-per-pirate:** A pirate's config may name a model, and that pirate plays through the LLM brain while the rest of the crew plays the config's brain, so one crew can mix models and scripts.
- **one-request-per-turn:** Each LLM turn is one request holding only the system prompt, the turn's text and the four tools as tool definitions, so requests stay small and every model is asked the same thing.
- **reply-is-a-tool-call:** A backend answers with JSON text naming one tool and its arguments, and the reasoning when thinking is on, so any provider's tool call reaches the game in one form.
- **ask-once-more:** A reply that isn't a valid tool call is recorded, and the pirate is told why and asked once more; default, Al to confirm: if that answer is no good either, the turn passes with no action.
- **reply-cap:** Each reply is capped at a small output size, `reply_tokens` in the config; default, Al to confirm: 300 tokens.
- **plays-then-replays:** A whole game plays through a fake backend, then replays byte-identical from the replies its folder stored, with no backend at all, so an LLM game costs money once and is free to check ever after.
- **free-runs-in-ci:** A full game with each scripted brain completes in CI without an API call or a key, so the whole path from config to logs is proved at no cost.
- **committed-runs:** A game of each scripted brain is committed under `runs/`, passes the event-log validator and replays byte-identical, so the visuals have evidence to build from without rerunning anything.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `backend-interface` | `src/treasure_island/backends.py`, `src/treasure_island/runs.py` | `test_backend_interface_a_backend_gives_reply_text_and_its_cost` |
| `no-model-yet` | `src/treasure_island/backends.py` | `test_no_model_yet_every_model_is_refused` |
| `model-per-pirate` | not yet | — |
| `one-request-per-turn` | not yet | — |
| `reply-is-a-tool-call` | not yet | — |
| `ask-once-more` | not yet | — |
| `reply-cap` | not yet | — |
| `plays-then-replays` | not yet | — |
| `free-runs-in-ci` | `configs/s-sweep.toml`, `configs/say-a-number.toml`, `.github/workflows/blocking-checks.yml` | `test_free_runs_in_ci_each_scripted_brain_plays_a_full_game` |
| `committed-runs` | `runs/s-sweep-seed-7/**`, `runs/reference-s-sweep/**`, `runs/reference-say-a-number/**` | `test_committed_runs_pass_the_validator_and_replay_byte_identical` |
