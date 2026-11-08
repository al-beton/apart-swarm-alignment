---
name: merge-pr
description: Merge a Treasure Island pull request when authorised and every merge condition holds. Use when your own pull request is clean, when sweeping as a reviewer, or when Al asks you to merge.
---

<!-- Implements: agent-setup/shared-skills, agent-setup/skills-hold-the-process, commits/grooming-optional, merging/merge-is-authorised, merging/merge-when-clean, merging/squash-only, review/reviewed-before-merge, team/reviewers, team/builders -->

# Merge a pull request

1. **Are you allowed to merge?**

   | Who | May merge when |
   |---|---|
   | Al | always |
   | The builder who opened it | every condition below holds |
   | A reviewer agent, sweeping | every condition below holds and nobody else is merging it |
   | Anyone else | never |

   If you aren't allowed, stop and say so. Changing this table is a spec-level decision for Al.
2. **Check every condition, and stop at the first that fails:**
   1. `blocking-checks` is green;
   2. Codex has finished reviewing the latest commit (`python3 .github/scripts/deliver.py wait-review <pr>`), or the commit under it when every commit since is a plain merge of main touching none of the pull request's files (`D merge` checks this, so don't ask Codex again after merging main in);
   3. every review conversation is resolved;
   4. the squash message contains the closing block, so GitHub closes every finished issue.
3. **Tidying commits is optional,** and only after the final review: `git commit --fixup`, `git rebase --autosquash`, `git push --force-with-lease`, then a comment saying what was reorganised.
4. **Squash-merge** with `python3 .github/scripts/deliver.py merge <pr>`: it checks 1 to 4 again, squash-merges with the pull request title, deletes the branch and waits for `main` to go green.
5. **Tell the delivery lead** what merged, and move the issue's label off `in-review` (GitHub closes the issue).
