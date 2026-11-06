# Research

- **hypothesis-first:** Each experiment states its question, arms, metrics and spending cap before it runs.
- **pilot-first:** Each experiment runs a one-seed pilot before any full run, and the full run waits for Al's yes.
- **spend-caps:** Every run of an experiment carries its spending cap, research spending stays within the day's cap Al sets, and going beyond either needs Al's yes.
- **loop-closes:** A finished experiment leaves its runs and its findings note committed, and the Manager gets a five-line summary of what it found.
- **results-from-logs:** Every number we report comes from a committed run's logs, never from memory or a console.
- **honest-limits:** Write-ups say plainly what an experiment can't show.
- **outputs-home:** Experiment specs and findings notes live in `experiments/`, and generated pages are not committed.
- **every-run-committed:** Every experiment run is committed under `runs/<experiment>/`; scratch smoke runs are the only exception.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `hypothesis-first` | `.agents/skills/review-pr/SKILL.md`, `.agents/skills/team/SKILL.md` | — |
| `pilot-first` | `.agents/skills/team/SKILL.md` | — |
| `spend-caps` | `.agents/skills/team/SKILL.md` | — |
| `loop-closes` | `.agents/skills/team/SKILL.md` | — |
| `results-from-logs` | `.agents/skills/review-pr/SKILL.md` | — |
| `honest-limits` | `.agents/skills/review-pr/SKILL.md` | — |
| `outputs-home` | `.agents/skills/team/SKILL.md` | — |
| `every-run-committed` | `.agents/skills/team/SKILL.md`, `.agents/skills/review-pr/SKILL.md` | — |
