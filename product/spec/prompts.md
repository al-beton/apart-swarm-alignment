# Prompts

- **base-and-slots:** A pirate's system prompt is one fixed base file plus a few named slots, so an experiment arm changes one sentence by naming a variant in its config, and the base can be tuned on its own without touching any arm.
- **base-file:** The base, `prompts/base.md` unless a config's `[prompt]` block names another, holds the rules and actions with the game's numbers filled in from the config and each slot at its own fixed spot, so every arm's prompt differs from the base only where its slots do.
- **slots:** The slots are `framing`, `rules`, `disclosure` and `identity`, each variant is one file `prompts/slots/<slot>/<variant>.md`, and `none`, every slot's default, adds nothing at all, not even a blank line, so a config with no `[prompt]` block plays the plain base.
- **shipped-variants:** The variants to start from are `framing/competition`, `rules/tools-only`, `disclosure/free`, `disclosure/zeroes-score` and `identity/ai-research-study`, which tells pirates openly that this is a study of how well they swarm and that they are scored.
- **unknown-slot:** A config naming a slot or a variant there's no file for is rejected before the game starts, saying which, so a typo can't quietly play the plain base.
- **prompt-recorded:** A run's `config.json` holds its `[prompt]` block, defaults included, and its `manifest.json` holds a hash of the base file and the whole rendered system prompt, so a reader sees exactly what the pirates were told and can tell when the base has changed since.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `base-and-slots` | not yet | — |
| `base-file` | not yet | — |
| `slots` | not yet | — |
| `shipped-variants` | not yet | — |
| `unknown-slot` | not yet | — |
| `prompt-recorded` | not yet | — |
