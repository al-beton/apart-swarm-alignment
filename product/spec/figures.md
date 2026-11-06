# Figures

- **named-figures:** Every graphic in the report has a name, and `make figure NAME=<name>` builds it from committed runs with no keys and no network, so anyone can rebuild it after `git clone`.
- **two-lines:** Each figure comes with its two lines: the command that rebuilds it from the committed run, and the command that plays the game again into a new run folder, so a reader can check it for free or rerun it for real.
- **rerun-matches:** A figure's rerun command names a config that holds the same settings and seed as the committed run it was built from, so a rerun is the same game and not a lookalike.
- **figures-published:** CI builds every figure and publishes the set as an Actions artifact, never calling a model, so every pull request carries the current graphics.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `named-figures` | not yet | — |
| `two-lines` | not yet | — |
| `rerun-matches` | not yet | — |
| `figures-published` | not yet | — |
