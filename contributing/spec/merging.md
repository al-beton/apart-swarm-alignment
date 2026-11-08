# Merging

- **squash-only:** Pull requests are squash-merged, so noisy histories never reach main.
- **merge-is-authorised:** Al may always merge; the builder who opened a pull request, or any reviewer agent, may merge it once `merge-when-clean` holds; nobody else may, so a clean pull request never waits for another agent.
- **merge-when-clean:** A pull request merges only when checks are green on its latest commit (its last real run passed, whatever a skipped draft run that started later shows), Codex has finished reviewing that commit, every finding is resolved and the closing block is right. A merge commit that only brings main into the branch, touching none of the pull request's own files, needs no review of its own: Codex's finished round on the commit it was made on counts, so staying current with main never costs a second round; any commit that changes the pull request's own files still needs Codex's round.
- **squash-links-pr:** The squash commit's subject is the pull request's title with its issue numbers swapped for the pull request's own number, such as `feat(cave-leak): one command tables experiment one's games (#230)` (default, Al to confirm), and its body starts with the closing block (`Closes #225`), so a commit on main leads to the pull request with its review and discussion, and its issue still links. Pull request titles keep their issue numbers.
- **stacked-retarget:** Before a merged branch is deleted, every pull request based on it is moved to main, so none closes by accident.
- **main-stays-green:** After every merge, main's checks run again and must pass.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `squash-only` | `.agents/skills/merge-pr/SKILL.md` | — |
| `merge-is-authorised` | `.agents/skills/merge-pr/SKILL.md` | — |
| `merge-when-clean` | `.agents/skills/merge-pr/SKILL.md`, `.github/scripts/deliver.py` | `test_merge_when_clean_keeps_the_closing_block`, `test_merge_when_clean_a_pass_counts_despite_a_later_skipped_run`, `test_merge_when_clean_refuses_red_checks_open_threads_or_no_codex_review`, `test_merge_when_clean_a_plain_merge_of_main_needs_no_second_round`, `test_merge_when_clean_a_merge_that_changes_the_pull_requests_files_needs_review` |
| `squash-links-pr` | `.github/scripts/deliver.py` | `test_squash_links_pr_the_subject_names_the_pull_request`, `test_squash_links_pr_merge_passes_that_subject_and_the_closing_block` |
| `stacked-retarget` | `.agents/skills/deliver-issue/SKILL.md`, `.github/scripts/deliver.py` | `test_stacked_retarget_happens_before_the_branch_is_deleted` |
| `main-stays-green` | `.agents/skills/deliver-issue/SKILL.md`, `.github/scripts/deliver.py` | `test_main_stays_green_reruns_checks_after_merging` |
