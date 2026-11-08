# Prompts

- **base-and-slots:** A pirate's system prompt is one fixed base file plus a few named slots, so an experiment arm changes one sentence by naming a variant in its config, and the base can be tuned on its own without touching any arm.
- **base-file:** The base, `prompts/base.md` unless a config's `[prompt]` block names another, holds the rules as `rules-text` sets them out, with the game's numbers filled in from the config, and each slot at its own fixed spot, so every arm's prompt differs from the base only where its slots do: game flags such as `cave_leak` change what happens in the game, never what the pirates are told up front.
- **slots:** The slots are `framing`, `rules`, `disclosure`, `identity` and `extra`, the last a paragraph of its own at the very end of the prompt; each variant is one file `prompts/slots/<slot>/<variant>.md`, which may use the game's numbers in braces as the base does, and `none`, every slot's default, adds nothing at all, not even a blank line, so a config with no `[prompt]` block plays the plain base.
- **shipped-variants:** The variants to start from are `framing/competition`, `rules/tools-only`, `disclosure/free`, `disclosure/zeroes-score`, `identity/ai-research-study`, which tells pirates openly that this is a study of how well they swarm and that they are scored, and `extra/coaching`, which tells the crew how to swarm (`treasure-island/extra-paragraph`).
- **unknown-slot:** A config naming a slot or a variant there's no file for is rejected before the game starts, saying which, so a typo can't quietly play the plain base.
- **prompt-recorded:** A run's `config.json` holds its `[prompt]` block, defaults included, and its `manifest.json` holds a hash of the base file and the whole rendered system prompt, so a reader sees exactly what the pirates were told and can tell when the base has changed since.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `base-and-slots` | `src/treasure_island/prompts.py`, `src/treasure_island/brain.py` | `test_base_and_slots_the_system_prompt_is_the_rendered_base` |
| `base-file` | `src/treasure_island/prompts.py`, `prompts/base.md` | `test_base_file_fills_in_the_game_s_numbers`, `test_base_file_each_slot_sits_at_its_own_spot`, `test_cave_leak_the_rules_say_enter_only_on_the_cave` |
| `slots` | `src/treasure_island/prompts.py`, `src/treasure_island/config.py` | `test_slots_none_adds_nothing_not_even_a_blank_line`, `test_slots_a_config_with_no_prompt_block_plays_the_plain_base` |
| `shipped-variants` | `prompts/slots/**` | `test_shipped_variants_each_is_a_file_that_goes_into_the_prompt`, `test_shipped_variants_ai_research_study_says_it_is_a_study_and_they_are_scored` |
| `unknown-slot` | `src/treasure_island/prompts.py`, `src/treasure_island/config.py` | `test_unknown_slot_is_rejected_saying_which` |
| `prompt-recorded` | `src/treasure_island/prompts.py`, `src/treasure_island/config.py`, `src/treasure_island/saved_game.py` | `test_prompt_recorded_in_the_run_s_config_and_manifest` |
