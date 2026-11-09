# Team

- **manager:** Al brings work to one manager agent, which turns what Al says into well-specced issues and priorities and relays decisions to the rest of the team, so Al never has to brief anyone twice.
- **specker:** Al also talks directly to a Specker session, which owns `product/spec/treasure-island.md`, so what the game should do is worked out with Al in one place.
- **visual-assets:** Al also talks directly to a Visual Assets session, which owns `assets/`, so how the game looks is worked out with Al in one place.
- **delivery-lead:** A delivery lead owns the issue queue: it decides what is built next, assigns each issue to one builder and keeps the queue's labels current.
- **builders:** One or two builders each deliver the issue they were assigned, from spec to a pull request that is green and reviewed by Codex, and merge it themselves once it is clean.
- **reviewers:** Reviewers sweep: they merge any clean pull request nobody merged, move stacked pull requests onto `main` when files overlap or one isn't clean, and keep `main` green; a full review is optional.
- **codex:** Codex reviews every pull request adversarially, independently of the agent that built it.
- **researcher:** A research agent uses the game to run experiments and surfaces findings worth Al's attention.
- **queue-labels:** Each open issue shows where it stands with one label, `ready`, `in-progress`, `in-review`, `blocked` or `on-hold`, so anyone can see the queue at a glance.
- **board-follows-labels:** The project board (Al's project 2) follows the queue labels by itself: whenever an issue is opened, labelled, unlabelled, closed or reopened, a workflow puts it on the board and sets its Status to its queue label's column (`ready` to Ready, `in-progress` to In progress, `in-review` to In review, `blocked` to Blocked, `on-hold` to On hold), Done once it is closed, and no Status if it has no queue label. The workflow reaches the board with a `PROJECT_TOKEN` secret Al adds (a fine-grained token with project write), never a key in the repository, and without that secret it does nothing.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `manager` | `.agents/skills/team/SKILL.md` | — |
| `specker` | `.agents/skills/team/SKILL.md` | — |
| `visual-assets` | `.agents/skills/team/SKILL.md` | — |
| `delivery-lead` | `.agents/skills/team/SKILL.md` | — |
| `builders` | `.agents/skills/team/SKILL.md`, `.agents/skills/deliver-issue/SKILL.md` | — |
| `reviewers` | `.agents/skills/team/SKILL.md`, `.agents/skills/merge-pr/SKILL.md` | — |
| `codex` | `.agents/skills/team/SKILL.md` | — |
| `researcher` | `.agents/skills/team/SKILL.md` | — |
| `queue-labels` | `.agents/skills/team/SKILL.md`, GitHub (labels) | — |
| `board-follows-labels` | `.github/workflows/board.yml`, `.github/scripts/board.py` | `test_board_follows_labels_each_queue_label_has_its_column`, `test_board_follows_labels_no_queue_label_clears_the_status`, `test_board_follows_labels_adds_the_issue_then_sets_its_status`, `test_board_follows_labels_the_workflow_runs_on_label_changes_with_the_secret` |
