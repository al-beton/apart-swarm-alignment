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
| `one-interface` | not yet | — |
| `scripted-sees-the-prompt` | not yet | — |
| `grid-sweep` | not yet | — |
| `counter` | not yet | — |
| `free-runs-in-ci` | not yet | — |
| `committed-runs` | not yet | — |
