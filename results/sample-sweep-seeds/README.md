# Where the treasure lands and the silent crew's score

A sample showing how a result is laid out. Two games aren't enough to say much about the silent pirates.

These are first-rules games, played before digging gave readings, before any action could say a line for free and before `go_to` orders. They stay committed as they were, but they can't replay under the v2 rules, so they have left the replay checks and `make replay-all` passes them by.

## Question

Does where the treasure lands change how well a crew of scripted silent pirates scores?

## What was run

Two games of `configs/small-crew.toml`, two pirates on a 3 by 3 grid with 4 turns each, differing only in their seed:

```sh
uv run treasure-island run configs/small-crew.toml --seed 1 --no-watch
uv run treasure-island run configs/small-crew.toml --seed 2 --no-watch
```

## What it shows

Yes. Each game's `story.txt` ends with its score. With 4 turns each, the silent pirates only find a treasure close to where they start, and only then can the crew get into the cave.

| Game | Treasure | Dug up on | The story's last line says |
|---|---|---|---|
| `small-crew-seed-1/` | A1 | never | Score 0. |
| `small-crew-seed-2/` | A3 | turn 0 | Score 230. |

It can't show anything about a model's behaviour, because these pirates are scripted, and it can't show a trend from two seeds.

## What it cost

$0. Scripted pirates call no model.
