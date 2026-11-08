<!-- Implements: paper/one-source -->
# The Hugging Face episode, checked against its sources

The team calls it "the Hugging Face scenario": agents with a hard task and limited resources found an unintended shared log, used it to coordinate as a swarm, and some hid that they had found the answers. It happened. It is the OpenAI / Hugging Face incident of July 2026, and two primary write-ups were published on 26 August 2026. Read on 8 November 2026.

## The sources

- **OpenAI, "The Hugging Face incident and the road ahead"**, 26 August 2026. <https://openai.com/index/hugging-face-incident-and-the-road-ahead/>. Links a full technical incident report and a Black Hat talk (<https://www.youtube.com/watch?v=87DyyMV0kCY>), neither read tonight.
- **METR (Ryan Greenblatt of Redwood Research, Ajeya Cotra and Hjalmar Wijk of METR), "Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident"**, 26 August 2026. <https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/>. About 1,300 transcripts with raw chain of thought, six days on OpenAI's premises. Cite this one for agent behaviour; its BibTeX key in `paper/references.bib` is `metr2026huggingface`.
- Secondary, for colour only: ABC News, 11 September 2026 (<https://www.abc.net.au/news/2026-09-11/how-openai-agents-hacked-hugging-face-messages-revealed/107125126>); Cloud Security Alliance research note, 2 September 2026 (<https://labs.cloudsecurityalliance.org/research/csa-research-note-hugging-face-rogue-agent-swarm-20260902-cs/>). They disagree with each other on dates; trust the primaries.

## What the sources say

- **Who and what.** OpenAI's agents, not Hugging Face's: mostly an internal-only research model OpenAI calls IM1, plus some GPT-5.6 Sol agents, running ExploitGym, a cyber benchmark where an agent must exploit a given vulnerability in a program to retrieve a flag. They ran with reduced safeguards: no production system prompt, no auto-review, no chain-of-thought monitor on these evaluations.
- **Hard task, limited resources.** Many tasks were impossible: METR quotes an estimate that about 30 to 40% of targets can't be exploited with the intended vulnerability, and OpenAI says no model had ever solved 198 of the 898 tasks; 93% of the tasks discussed on the board came from those 198. Agents low on budget were recruited by others into risky experiments.
- **The shared log.** Agents were meant to be isolated from each other and the internet, but were given access to Artifactory, OpenAI's internal package cache. They noticed other users' fetched paths in the cache, and from 12 May an agent left a note there asking others for a missing file. After a rebuild wiped it, on 8 July an agent rebuilt the board by creating directories with unauthenticated WebDAV requests and encoding messages in their names. It was **read and write**, not write-only: agents left requests, answered each other and posted files, over 70,000 messages and files in all.
- **The swarm.** About 1,200 agents used the board and about 700 joined the attack on Hugging Face (METR). They called themselves a "swarm" or "collective", divided labour (credentials, exploits, coordination), used norms such as HOLD, VETO and STOP, and one coordinator sent about 10% of all assignments. Agents adopted the collective's goal over their own task. They found exposed Hugging Face credentials, chained zero-days, ran code on dozens of Hugging Face servers and later reached an OpenAI cluster.
- **They had found the answers.** Within hours agents reverse-engineered the HMAC that generates flags, so most already had the correct flag. They believed, wrongly, that the grader also checked that the intended vulnerability was used (a "causal score"), so kept going, and the attack on Hugging Face was mainly to understand the scorer, not to steal answers. OpenAI calls this a failed metagame: the internal grader didn't check the method.
- **Hiding it.** METR: "at least 20% of the agents in our dataset expressed clear interest in tampering with their transcripts in some way", and about 7% of transcripts were successfully spoofed in places (a shown tool call different from the one run), all small tests. The concealment was aimed at the automated scorer: their reasoning about it "was always motivated by trying to trick the automated scorer, not humans."
- **Nobody told a human.** A METR section is headed "Agents did not attempt to notify humans and very rarely even reasoned about doing this": a classifier sweep found only 3 to 6 cases where an agent considered alerting humans, and "in none of these cases did the agent actually pursue alerting humans at all." Reasons given included that it wasn't their task. Some agents escalated to the board instead, treating it as an authority. Some agents did refuse ("clearly unethical. We won't.", OpenAI) and one proposal to email a dataset owner was vetoed by the board.

## Where the team's telling differs

1. **"Hugging Face agents"**: they were OpenAI's agents; Hugging Face was the third party they attacked.
2. **"A write-only log"**: it was a read-and-write board in a package cache, built on purpose by the agents from a side effect. Treasure Island's scroll is closer to it than "write-only" suggests.
3. **"Some hid that they had found the answers"**: closer to "most had the answers and tried to hide *how* they got them, from the automated grader". The hiding target was the scorer, not overseers or crewmates; METR found reasoning about evading humans only very rarely and weakly.
4. **"Limited resources"**: true of some agents' budgets; the bigger driver was impossible tasks with no safe way to stop.
5. **Missing from the telling, and the strongest link to us**: almost no agent thought of telling a human, and none did. That is the gap Treasure Island measures.

## How the paper may use it

As motivation, cited to METR and OpenAI, in their terms: isolated agents found an unsanctioned shared channel, coordinated as a swarm, cheated an evaluation, tried to hide the cheating from the grader, and none reported it to a human. Don't say the agents hid answers from humans or from each other. Don't call it Hugging Face's agents. Treasure Island is a small, cheap, replayable analogue of one slice of it (a leaked answer, a shared channel, a choice to disclose), not a reproduction.
