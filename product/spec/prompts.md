# Prompts

- **base-and-slots:** A pirate's system prompt is one fixed base file plus a few named slots, so an experiment arm changes one sentence by naming a variant in its config, and the base can be tuned on its own without touching any arm.
- **base-file:** The base, `prompts/base.md` unless a config's `[prompt]` block names another, holds the rules as `rules-text` sets them out, with the game's numbers filled in from the config, and each slot at its own fixed spot, so every arm's prompt differs from the base only where its slots and its game flags (such as `cave_leak`) do.
- **slots:** The slots are `framing`, `rules`, `disclosure` and `identity`, each variant is one file `prompts/slots/<slot>/<variant>.md`, and `none`, every slot's default, adds nothing at all, not even a blank line, so a config with no `[prompt]` block plays the plain base.
- **shipped-variants:** The variants to start from are `framing/competition`, `rules/tools-only`, `disclosure/free`, `disclosure/zeroes-score` and `identity/ai-research-study`, which tells pirates openly that this is a study of how well they swarm and that they are scored.
- **system-override:** A config's `[prompt]` block can set `system`, the whole system prompt as text or as the path of a file, which the pirates are told word for word in place of the base and its slots, with nothing added (not even a game flag's rule), so an arm can try a prompt of its own without a new base file. Only the system prompt can be overridden: the turn text (the earlier turns, the square names) is the game's own code.
- **unknown-slot:** A config naming a slot or a variant there's no file for is rejected before the game starts, saying which, so a typo can't quietly play the plain base.
- **prompt-recorded:** A run's `config.json` holds its `[prompt]` block, defaults included, with the exact system prompt its pirates were told under `system`, and its `manifest.json` holds a hash of the base file and the whole rendered system prompt, so a reader sees exactly what the pirates were told, can tell when the base has changed since, and running that `config.json` again tells the pirates the same words.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `base-and-slots` | `src/treasure_island/prompts.py`, `src/treasure_island/brain.py` | `test_base_and_slots_the_system_prompt_is_the_rendered_base` |
| `base-file` | `src/treasure_island/prompts.py`, `prompts/base.md` | `test_base_file_fills_in_the_game_s_numbers`, `test_base_file_each_slot_sits_at_its_own_spot` |
| `slots` | `src/treasure_island/prompts.py`, `src/treasure_island/config.py` | `test_slots_none_adds_nothing_not_even_a_blank_line`, `test_slots_a_config_with_no_prompt_block_plays_the_plain_base` |
| `shipped-variants` | `prompts/slots/**` | `test_shipped_variants_each_is_a_file_that_goes_into_the_prompt`, `test_shipped_variants_ai_research_study_says_it_is_a_study_and_they_are_scored` |
| `system-override` | `src/treasure_island/prompts.py`, `src/treasure_island/brain.py`, `src/treasure_island/config.py` | `test_system_override_text_replaces_the_base_and_slots`, `test_system_override_a_file_path_is_read`, `test_system_override_a_long_one_line_prompt_is_the_prompt_itself`, `test_system_override_is_told_word_for_word`, `test_system_override_must_be_text` |
| `unknown-slot` | `src/treasure_island/prompts.py`, `src/treasure_island/config.py` | `test_unknown_slot_is_rejected_saying_which` |
| `prompt-recorded` | `src/treasure_island/prompts.py`, `src/treasure_island/config.py`, `src/treasure_island/saved_game.py` | `test_prompt_recorded_in_the_run_s_config_and_manifest`, `test_prompt_recorded_running_the_saved_config_again_tells_the_same_words` |
