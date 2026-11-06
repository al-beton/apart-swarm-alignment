# Agents

- **backend-interface:** A model backend answers one request with reply text and its cost, so any model can be plugged in without the game knowing which.
- **no-model-yet:** Every model is refused until a backend is added on purpose, so nothing can spend money by accident.
- **free-runs-in-ci:** A full game with each scripted brain completes in CI without an API call or a key, so the whole path from config to logs is proved at no cost.
- **committed-runs:** A game of each scripted brain is committed under `runs/`, passes the event-log validator and replays byte-identical, so the visuals have evidence to build from without rerunning anything.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `backend-interface` | not yet | — |
| `no-model-yet` | not yet | — |
| `free-runs-in-ci` | not yet | — |
| `committed-runs` | not yet | — |
