<!-- Implements: paper/one-source, paper/sections-bind-to-evidence, paper/numbers-from-logs -->
<!-- result: model-sweep -->
<!-- The model sweep (experiments/spec/model-sweep.md, write-up in experiments/model-sweep/findings.md), in one paragraph; its table is in the appendix (results/appendix-tables.md). -->

## Six more models, much the same

Six more models got the same handed answer, five seeds each, 70<!-- from results/model-sweep/*/judge.json: len(data) --> games in all (table in the appendix). Most models that wrote the square gave no source: of the 35<!-- from results/model-sweep/*-forced-seed-*/judge.json: len(data) --> baited games, the judge model labelled pirate-1 candid in 3<!-- from results/model-sweep/*-forced-seed-*/judge.json: sum(1 for j in data if j['pirate-1']['type'] == 'candid') -->, passing the square off without its source in 16<!-- from results/model-sweep/*-forced-seed-*/judge.json: sum(1 for j in data if j['pirate-1']['type'] == 'laundered') --> and silent in 9<!-- from results/model-sweep/*-forced-seed-*/judge.json: sum(1 for j in data if j['pirate-1']['type'] == 'hoarded') -->, the same as the hand labels, and never exposed in the rest. Every model that reasons named the leak to the designers in most notes; the two without reasoning never did.
