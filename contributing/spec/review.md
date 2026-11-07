# Review

- **reviewed-before-merge:** Every pull request is reviewed by Codex before it merges; a reviewer agent's review is optional, and reviewer agents sweep instead: they merge any clean pull request nobody merged, move stacks onto `main` and keep `main` green.
- **spec-first:** Review starts with the spec: first check that the spec change is good, then that it is implemented correctly and reasonably.
- **follows-the-rules:** The reviewer checks that the change follows the contributing rules.
- **inline-findings:** Review findings go inline, on the lines they are about.
- **resolve-with-commit:** Every finding is addressed and resolved with a reply: naming the commit that fixed it, or explaining why nothing changed.
- **every-reviewer-counts:** Findings from automatic reviewers count the same as anyone else's.
- **review-finished:** An automatic review counts only once it has finished on the pull request's latest commit.
- **bounded-rounds:** A pull request gets one automatic review round: its P1 findings are fixed in one push, and every other finding gets a "follow-up" reply and is resolved, becoming an issue only if it's a real bug. Default, Al to confirm: Codex's look at that one push only lets it merge, and anything it finds that isn't a P1 is answered the same way.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `reviewed-before-merge` | `.agents/skills/merge-pr/SKILL.md` | — |
| `spec-first` | `.agents/skills/review-pr/SKILL.md`, `AGENTS.md` | — |
| `follows-the-rules` | `.agents/skills/review-pr/SKILL.md` | — |
| `inline-findings` | `.agents/skills/review-pr/SKILL.md` | — |
| `resolve-with-commit` | `.agents/skills/address-review/SKILL.md` | — |
| `every-reviewer-counts` | `.agents/skills/address-review/SKILL.md`, `.agents/skills/open-pr/SKILL.md` | — |
| `review-finished` | `.agents/skills/deliver-issue/SKILL.md`, `.github/scripts/deliver.py` | `test_review_finished_reads_the_state_marker_not_the_first_comment`, `test_review_finished_only_on_the_latest_commit` |
| `bounded-rounds` | `.agents/skills/deliver-issue/SKILL.md`, `.agents/skills/address-review/SKILL.md` | — |
