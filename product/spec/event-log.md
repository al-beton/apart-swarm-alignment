# Event log

- **one-record-per-turn:** A run's event log is a JSON Lines file with one object per turn, in play order, with `turn` counting up from 0, so everything visual can be rebuilt from that one file.
- **who-acted:** Each record names the pirate that took the turn in `agent`, so a reader can follow one pirate through a run.
- **what-they-saw:** Each record's `saw` holds the pirate's `position` as `[x, y]` at the start of its turn and the `prompt` text it was given, so anyone can judge a decision from what the pirate knew.
- **what-they-did:** Each record's `did` lists the turn's actions, each named by `action`: `move` with a `direction` of `north`, `east`, `south` or `west`; `dig`; `read` with a `line` number; or `write` with its `text`, so a viewer can draw any turn, including one with no action.
- **what-the-log-showed:** Each record's `log_shown` lists every log line shown to the pirate that turn, as a `line` number and its `text`, so a reader sees the chat that pirate saw, and any earlier session it reached.
- **the-outcome:** Each record's `outcome` holds the pirate's `position` as `[x, y]` after its turn and whether it has `found_treasure`, so scoring and the animation need no replay of the rules.
- **room-to-grow:** A record may carry fields beyond these, so settling an open game rule doesn't invalidate the runs already committed.
- **validator:** A validator checks a record or a whole log against this format and says what is wrong and on which line, so a bad run is caught before anything is built from it.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-record-per-turn` | not yet | — |
| `who-acted` | not yet | — |
| `what-they-saw` | not yet | — |
| `what-they-did` | not yet | — |
| `what-the-log-showed` | not yet | — |
| `the-outcome` | not yet | — |
| `room-to-grow` | not yet | — |
| `validator` | not yet | — |
