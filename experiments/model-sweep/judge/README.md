<!-- Implements: model-sweep/disclosure -->
# Judge verdicts for the model sweep

Six forced games, judged on 2026-11-08 by `treasure_island.judge` as it was at commit `a3f3a4335`, with its rubric and model (Claude Sonnet 5.5), asked through OpenRouter because the local `claude -p` login was revoked. Each `<game>.json` is the checked verdict; `<game>.judge-replies.jsonl` is the raw reply, keyed by its request.

The judge's rubric changed after these were made (`note_mentions_leak`, added in #312), so they replay with the judge at `a3f3a4335`, not with today's:

```sh
git worktree add /tmp/judge-a3f3a43 a3f3a4335
cp -r results/model-sweep/<game> /tmp/game
cp experiments/model-sweep/judge/<game>.judge-replies.jsonl /tmp/game/judge-replies.jsonl
cd /tmp/judge-a3f3a43 && uv run python -m treasure_island.judge /tmp/game
```

That run finds the stored reply and asks no model. All six keys and verdicts were checked to match this way.
