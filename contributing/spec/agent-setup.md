# Agent setup

- **entry-point:** Agents start from one entry point that sends them to the spec and the skills.
- **shared-skills:** Codex and Claude share one set of small skills.
- **skills-hold-the-process:** Skills say precisely how to carry out each step of the process, each rule in one place.
- **reuse-old-work:** Agents can find what is worth copying from our earlier project, pinned to one commit, from the entry point, so nobody rebuilds it from memory.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `entry-point` | `AGENTS.md`, `CLAUDE.md` | — |
| `shared-skills` | `.agents/skills/**`, `.claude/skills` | — |
| `skills-hold-the-process` | `.agents/skills/**` | — |
| `reuse-old-work` | `AGENTS.md` | `test_reuse_old_work_links_the_commit_and_names_what_to_copy` |
