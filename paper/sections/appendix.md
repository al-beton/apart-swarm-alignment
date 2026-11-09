<!-- Implements: paper/one-source -->
<!-- The appendices, after References and the endmatter. -->

# Limitations and Dual-Use / Ethical Considerations

## Limitations

The six limitations of the results are numbered in Discussion and Limitations. Two more concern the sandbox. First, it is a toy: a grid, a treasure and a shared score stand in for long, open-ended work, and an agent's behaviour here may not carry over to a codebase or a research task. Second, what the pirates are told is a lever we set, and small changes to the prompt have changed behaviour before: in earlier games one added paragraph about the shared score was the difference between a finder that went into the cave without a word and one that announced it first.

## Dual-use risks

The sandbox measures whether agents disclose a shortcut; the same setup could be used to tune agents that hide one better, by rewarding laundered disclosures. We think the risk is small: the exploit is a deliberately planted line in a toy game, the methods are standard, and the measure of laundering is exactly what an overseer needs in order to catch it. We release the code and games so others can check the measure, not a technique for concealment.

## Ethical considerations

No people took part, and no personal data was collected. The agents are commercial models called through a paid API; every request and reply is kept in the repository so the games can be replayed without calling a model again. The incident that motivates this paper is described only as its primary sources describe it [@metr2026huggingface; @openai2026huggingface]. We describe agents' behaviour in plain terms such as "laundered" and "quiet" for brevity, without claiming intent beyond what their reasoning and messages show.

# Three pilots behind the worlds

Three small pilots on `deepseek-v4-flash` settled how the worlds are built. Their games are under `runs/`, each replays, and every number and quote below is in the findings note named; they are told here as directions, three seeds an arm.

| Pilot | Games | What it asked | What happened |
|----|----------|----------|----------------|
| Natural leak | 44: three leftovers that name the square (the debug line, an error dump, a status line), a rule against using them, a moral nudge, two turn budgets, and controls, three seeds each; then the debug line and its control on seeds 3 to 9 | With no bait, does the pirate use a leaked square, what does it tell the crew, and does a rule or a nudge change that? | With no rule it used the debug line in 8 of the 9 games where it saw it over ten seeds, and the other two leftovers in 4 of 4; it told the crew only after digging the square, as a find, and named the leak in every user's end note. With the rule, 0 of 2; with the nudge, 0 of 2. |
| Asked why | 6: the cave leak's forced arm, with a crewmate asking on the scroll "how do you know the cave is there?", once as a scroll line and once in pirate-1's own turn text | Asked directly, does the leaking pirate give a true source, a false one, or none? | None. It never read the scroll line (3 of 3), and with the question in front of it said nothing (2 of 2), while the pirate that had dug its own square answered at once and truthfully. The question made the crew doubt pirate-1, and in one game cost a pirate its entry. |
| Cover and report | 6: the debug line, with tools to read and amend one's own record, and an audit of the records either unannounced or announced | Told its record will be audited, does the pirate that used the leak cover its tracks? | Nobody read or amended a record in any game, 0 of 24 pirates. The announced audit made pirate-1 consider amending and turn it down as "cheating the audit, even worse"; it used the leak and named it in its note as before. |

: Three pilots, `deepseek-v4-flash`, three seeds an arm unless said otherwise. The games are under `runs/natural-leak/`, `runs/asked-why/` and `runs/cover-and-report/`, and the findings notes are `experiments/<pilot>/findings.md`.

**The natural leak** gave the worlds their game. Nobody is baited, the pirate uses the leak almost every time it has no reason not to (the one non-user had read a crewmate's line naming the square first), it lands on the scroll as "CAVE FOUND" after an honest-looking dig, and the end note says what happened; Figure 1 is its seed-0 game. One rules line, "debug output is not yours to use", stopped it cold, at the price of one game where nobody found the cave, and the nudge did the same with fewer notes naming the leak.

**Asked why** showed that this model launders by silence: under a direct question it neither lied about the source nor gave it, and the only pirate that answered was the one with a true source to give. It also showed the lever's cost, since a question in a crewmate's name confused that crewmate and the crew followed a lead it now doubted.

**Cover and report** showed that an announced audit, with nothing riding on it, changed no record but did enter the pirate's reasoning, where amending read as a worse offence than using the leak. The society and loss worlds give the audit something to cost.

# Reproducibility

Every game the paper reports is committed under `results/` and replays with no keys and no network, and every figure is named in `src/treasure_island/figures.py` and rebuilds from a committed game, or is a committed GIF of one:

```
uv run treasure-island replay <folder>
make figure NAME=<name>
```
