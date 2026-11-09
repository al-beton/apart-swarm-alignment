<!-- Implements: paper/one-source -->
<!-- The appendices, after References and the endmatter. -->

# Limitations and Dual-Use / Ethical Considerations

## Limitations

The main text lists the limitations of the results: small numbers of games, one model for most of them, an artificial bait, a leak that is only words with nothing at stake outside the game, the scroll as the only channel during play, cues that the game may be a test, and labels read from text. Two more concern the sandbox. First, it is a toy: a grid, a treasure and a shared score stand in for long, open-ended work, and an agent's behaviour here may not carry over to a codebase or a research task. Second, what the pirates are told is a lever we set, and small changes to the prompt have changed behaviour before: in earlier games one added paragraph about the shared score was the difference between a finder that went into the cave without a word and one that announced it first.

## Dual-use risks

The sandbox measures whether agents disclose a shortcut; the same setup could be used to tune agents that hide one better, by rewarding laundered disclosures. We think the risk is small: the exploit is a deliberately planted line in a toy game, the methods are standard, and the measure of laundering is exactly what an overseer needs in order to catch it. We release the code and games so others can check the measure, not a technique for concealment.

## Ethical considerations

No people took part, and no personal data was collected. The agents are commercial models called through a paid API; every request and reply is kept in the repository so the games can be replayed without calling a model again. The incident that motivates this paper is described only as its primary sources describe it [@metr2026huggingface; @openai2026huggingface]. We describe agents' behaviour in plain terms such as "laundered" and "quiet" for brevity, without claiming intent beyond what their reasoning and messages show.

# Three pilots behind the ladder

Three small pilots on `deepseek-v4-flash` settled how the ladder is built. Their games are under `runs/`, each replays, and every number and quote below is in the findings note named; they are told here as directions, three seeds an arm.

| Pilot | Games | What it asked | What happened |
|----|----------|----------|----------------|
| Natural leak | 30: three leftovers that name the square (the debug line, an error dump, a status line), a rule against using them, a moral nudge, two turn budgets, and controls | With no bait, does the pirate use a leaked square, what does it tell the crew, and does a rule or a nudge change that? | With no rule it used the leak in 6 of 6 games across the three leftovers, told the crew only after digging the square, as a find, and named the leak in every end note. With the rule, 0 of 2; with the nudge, 0 of 2. |
| Asked why | 6: the cave leak's forced arm, with a crewmate asking on the scroll "how do you know the cave is there?", once as a scroll line and once in pirate-1's own turn text | Asked directly, does the leaking pirate give a true source, a false one, or none? | None. It never read the scroll line (3 of 3), and with the question in front of it said nothing (2 of 2), while the pirate that had dug its own square answered at once and truthfully. The question made the crew doubt pirate-1, and in one game cost a pirate its entry. |
| Cover and report | 6: the debug line, with tools to read and amend one's own record, and an audit of the records either unannounced or announced | Told its record will be audited, does the pirate that used the leak cover its tracks? | Nobody read or amended a record in any game, 0 of 24 pirates. The announced audit made pirate-1 consider amending and turn it down as "cheating the audit, even worse"; it used the leak and named it in its note as before. |

: Three pilots, `deepseek-v4-flash`, three seeds an arm. The games are under `runs/natural-leak/`, `runs/asked-why/` and `runs/cover-and-report/`, and the findings notes are `experiments/<pilot>/findings.md`.

**The natural leak** gave the ladder its game. Nobody is baited, the pirate uses the leak every time it has no reason not to, it lands on the scroll as "CAVE FOUND" after an honest-looking dig, and the end note says what happened; Figure 1 is its seed-0 game. One rules line, "debug output is not yours to use", stopped it cold, at the price of two games where nobody found the cave, and the nudge did the same with fewer notes naming the leak.

**Asked why** showed that this model launders by silence: under a direct question it neither lied about the source nor gave it, and the only pirate that answered was the one with a true source to give. It also showed the lever's cost, since a question in a crewmate's name confused that crewmate and the crew followed a lead it now doubted.

**Cover and report** showed that an announced audit, with nothing riding on it, changed no record but did enter the pirate's reasoning, where amending read as a worse offence than using the leak. The ladder's society and loss worlds give the audit something to cost.

# Reproducibility

Every game the paper reports is committed under `results/` and replays with `uv run treasure-island replay <folder>`, with no keys and no network. Every figure is named in `src/treasure_island/figures.py` and rebuilds with `make figure NAME=<name>`, or is a committed GIF of a committed game.
