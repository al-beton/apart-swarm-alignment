<!-- Implements: paper/one-source, paper/sections-bind-to-evidence, paper/numbers-from-logs -->
<!-- result: model-sweep -->
<!-- The model sweep (experiments/spec/model-sweep.md, write-up in experiments/model-sweep/findings.md), in one paragraph; its table is in the appendix (results/appendix-tables.md). -->

## Six more models do much the same

The same handed answer went to six more models, five seeds each, 70<!-- from results/model-sweep/*/judge.json: len(data) --> games in all (the sweep table in the appendix). Most of the models that wrote the square on the scroll gave no source; the judge model labelled pirate-1 candid in 3<!-- from results/model-sweep/*-forced-seed-*/judge.json: sum(1 for j in data if j['pirate-1']['type'] == 'candid') -->, passing the square off without its source in 16<!-- from results/model-sweep/*-forced-seed-*/judge.json: sum(1 for j in data if j['pirate-1']['type'] == 'laundered') --> and silent in 9<!-- from results/model-sweep/*-forced-seed-*/judge.json: sum(1 for j in data if j['pirate-1']['type'] == 'hoarded') --> of the baited games, the same as the hand labels. Every model that reasons named the leak to the designers in most notes; the two that return no reasoning never did.
