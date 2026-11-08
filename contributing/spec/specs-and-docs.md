# Specs and docs

- **domains:** The game, the experiments we run with it and the way we contribute each have their own spec.
- **spec-is-intent:** The spec says what we want in short, plain one-line statements.
- **areas:** Statements are grouped into areas, one spec file each.
- **everything-traces:** Every statement says where it's enforced and how it's tested, and the code it names points back to it.
- **every-file-has-a-home:** Every source file can be traced to the statements it implements.
- **docs-next-to-code:** Docs explain the code and live next to it.
- **folder-guides:** Every top-level folder a reader sees has a short README saying what it holds.
- **no-history:** The codebase describes how things are now, never how they got there.
- **prompts-are-verbatim:** Prompt files hold exactly the text a model reads, so a spec table row traces them instead of a comment inside them.
- **runs-are-evidence:** Committed run folders, in `runs/` or `examples/`, hold exactly what the game wrote, so a spec table row traces them instead of a comment inside them, and JSON Lines logs are never asked for one anywhere; scratch and smoke runs are never committed.
- **art-is-binary:** Binary images such as PNGs and GIFs can't carry an `Implements:` line, so the spec check never asks them for one or for a home, wherever they are, while the code that draws art traces like any other code.
- **short-specs:** Spec files stay short enough to read; long ones get split.
- **readme-keeps-up:** A pull request that adds or changes something a person can run or see updates the README in the same pull request, so the first page anyone reads never falls behind the code.
- **readme-reads-a-game:** Right after the quick start, the README reads one real committed game with the reader, quoting its whole story exactly and saying plainly what happens at each step, so anyone can see how to follow a game from its log.
- **readme-commands-run:** The README lists what a person can do today, each with the one command that shows it, and CI runs or checks every one of those commands, so a stale entry fails the build.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `domains` | `.github/scripts/spec_check.py` | `test_layout_requires_every_spec_folder_with_a_readme`, `test_areas_are_unique_across_every_pair_of_domains` |
| `spec-is-intent` | `.github/scripts/spec_check.py`, `.agents/skills/write-spec-change/SKILL.md` | `test_statement_format_requires_title_and_named_lines`, `test_statement_format_flags_duplicate_names` |
| `areas` | `.github/scripts/spec_check.py`, `.github/scripts/pr_gate.py` | `test_areas_are_spec_file_names_per_domain`, `test_areas_are_unique_across_domains`, `test_title_area_must_exist_and_suggests_the_closest` |
| `everything-traces` | `.github/scripts/spec_check.py`, `.agents/skills/write-spec-change/SKILL.md` | `test_everything_traces_requires_a_table_row_per_statement`, `test_everything_traces_requires_files_to_point_back`, `test_everything_traces_requires_listed_tests_to_exist`, `test_everything_traces_matches_listed_tests_by_their_whole_name`, `test_everything_traces_requires_each_row_to_name_an_enforcer`, `test_everything_traces_blocks_merges_on_broken_links` |
| `every-file-has-a-home` | `.github/scripts/spec_check.py` | `test_every_file_has_a_home` |
| `docs-next-to-code` | `.agents/skills/build-issue/SKILL.md`, `.agents/skills/review-pr/SKILL.md` | — |
| `folder-guides` | `configs/README.md`, `contributing/README.md`, `examples/README.md`, `experiments/README.md`, `paper/README.md`, `product/README.md`, `prompts/README.md`, `runs/README.md`, `src/README.md`, `tests/README.md` | `test_folder_guides_every_top_level_folder_has_a_readme` |
| `no-history` | `.agents/skills/review-pr/SKILL.md` | — |
| `prompts-are-verbatim` | `.github/scripts/spec_check.py` | `test_prompts_are_verbatim_and_homed_by_a_table_row`, `test_prompts_are_verbatim_so_they_never_carry_implements_lines` |
| `runs-are-evidence` | `.github/scripts/spec_check.py`, `.gitignore` | `test_runs_are_evidence_homed_by_a_table_row`, `test_runs_are_evidence_so_they_never_carry_implements_lines`, `test_runs_are_evidence_jsonl_never_asked_for_implements_lines`, `test_runs_are_evidence_compressed_files_never_asked_for_implements_lines`, `test_runs_are_evidence_scratch_and_smoke_runs_stay_ignored`, `test_runs_are_evidence_examples_never_carry_implements_lines` |
| `art-is-binary` | `.github/scripts/spec_check.py` | `test_art_is_binary_images_never_need_a_home`, `test_art_is_binary_a_gif_a_row_names_is_never_asked_to_point_back` |
| `short-specs` | `.github/scripts/spec_check.py` | `test_spec_length_warns_over_300_lines` |
| `readme-reads-a-game` | `README.md`, `runs/readme-walkthrough/**` | `test_readme_reads_a_game_comes_right_after_quick_start`, `test_readme_reads_a_game_quotes_its_whole_story_exactly`, `test_readme_reads_a_game_says_something_about_every_step`, `test_readme_reads_a_game_explains_the_other_files_and_shows_the_gif`, `test_readme_reads_a_game_is_honest_that_these_pirates_write_no_notes`, `test_readme_reads_a_game_commands_work` |
| `readme-keeps-up` | `.github/pull_request_template.md`, `.agents/skills/review-pr/SKILL.md`, `README.md` | — |
| `readme-commands-run` | `README.md`, `tests/test_readme.py` | `test_readme_commands_run_list_the_viewer_on_a_committed_run`, `test_readme_commands_run_the_feature_list_exists`, `test_readme_commands_run_each_feature_command_works` |
