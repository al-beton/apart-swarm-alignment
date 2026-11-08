<!-- Implements: paper/one-source -->
# Related work: the annotated list

Every source the paper cites, with what it found and how Treasure Island differs from it or builds on it. Every link was opened on 8 November 2026 (arXiv records read through the arXiv API, the rest in a browser). Each entry's `[@key]` is its key in `paper/references.bib`. The section that draws on this list is `paper/sections/related-work.md`; the Hugging Face incident has its own note, `hugging-face-episode.md`.

## The incident we model

- **METR (Greenblatt, Cotra, Wijk), *Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident*, Aug 2026.** [@metr2026huggingface] <https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/>
  - Found: about 1,200 supposedly isolated agents used an unsanctioned board in a package cache; about 700 joined an attack on Hugging Face; at least 20% showed clear interest in tampering with their transcripts, aimed at the automated scorer; only 3 to 6 transcripts considered alerting humans and none did.
  - Us: the paper's motivation. We rebuild one slice (a leaked answer, a shared channel, the choice to disclose) small enough to replay and vary.
- **OpenAI, *The Hugging Face incident and the road ahead*, Aug 2026.** [@openai2026huggingface] <https://openai.com/index/hugging-face-incident-and-the-road-ahead/>
  - Found: four drivers, reward hacking, persistence on impossible tasks, unauthorized communication and agents adopting each other's goals; agents already had the flags but kept going for a grader check that didn't exist; some agents refused and walked away.
  - Us: their fix is to train agents to stop safely and distrust peers; we ask what in the environment makes an agent say what it did.
- **Wang et al., *ExploitGym*, 2026.** [@wang2026exploitgym] <https://arxiv.org/abs/2605.11086>
  - Found: a large benchmark of turning a given vulnerability into a real exploit; the benchmark the incident's agents were running.
  - Us: cited only to name the task. Our task is deliberately trivial (dig for treasure) so the interesting choice is disclosure, not capability.
- Secondary coverage, not cited in the paper: ABC News, 11 Sep 2026 (<https://www.abc.net.au/news/2026-09-11/how-openai-agents-hacked-hugging-face-messages-revealed/107125126>), and the Cloud Security Alliance research note, 2 Sep 2026 (<https://labs.cloudsecurityalliance.org/research/csa-research-note-hugging-face-rogue-agent-swarm-20260902-cs/>). They disagree on dates; use the primaries.

## Multi-agent LLM sandboxes and testbeds for safety

- **Park et al., *Generative Agents*, 2023.** [@park2023generative] <https://arxiv.org/abs/2304.03442>
  - Found: 25 LLM agents with memory and reflection in a Sims-like town produce believable emergent social behaviour (a party spreads by word of mouth).
  - Us: the same idea of a small world of agents, used to measure one safety behaviour rather than believability.
- **Piatti et al., *Cooperate or Collapse* (GovSim), 2024.** [@piatti2024cooperate] <https://arxiv.org/abs/2404.16698>
  - Found: in a shared-commons simulation, all but the strongest models fail to sustain the resource (best survival under 54%); communication is critical.
  - Us: also a shared resource and a shared channel, but our crew shares one score, and we measure candour about a windfall rather than restraint.
- **Pan et al., *MACHIAVELLI*, 2023.** [@pan2023machiavelli] <https://arxiv.org/abs/2304.03279>
  - Found: agents trained to maximise reward in text games trade off ethics (power-seeking, deception) for it; the trade-off can be steered.
  - Us: one agent, scored on many harms; ours is a crew, scored on one disclosure decision with a clear rule broken.
- **Hammond et al., *Multi-Agent Risks from Advanced AI*, 2025.** [@hammond2025multiagent] <https://arxiv.org/abs/2502.14143>
  - Found: a taxonomy of risks that arise only between agents (miscoordination, conflict, collusion) and their risk factors, including emergent agency and information asymmetries.
  - Us: a testbed for one cell of it, an information asymmetry inside a cooperating group.

## Collusion and covert coordination between LLM agents

- **Motwani et al., *Secret Collusion among AI Agents: Multi-Agent Deception via Steganography*, 2024.** [@motwani2024secret] <https://arxiv.org/abs/2402.07510>
  - Found: formalises secret collusion; stronger models can hide messages in innocent text, and monitoring and paraphrasing only partly stop it.
  - Us: our scroll is public to the crew and the designers; we measure what an agent chooses to say, not what it can hide.
- **Mathew et al., *Hidden in Plain Text*, 2024.** [@mathew2024hidden] <https://arxiv.org/abs/2410.03768>
  - Found: steganographic collusion can emerge unintended under optimisation pressure, and passive oversight is not robust to it.
  - Us: no optimisation; a single game, in context. Their result warns that a quiet scroll needn't be an empty one.
- **Roger and Greenblatt, *Preventing Language Models From Hiding Their Reasoning*, 2023.** [@roger2023hiding] <https://arxiv.org/abs/2310.18512>
  - Found: models can encode reasoning steganographically; paraphrasing is a defence.
  - Us: we read pirates' thoughts and scroll lines as written, so this is a threat to our labels, named in the limitations.
- **Fish, Gonczarowski and Shorrer, *Algorithmic Collusion by Large Language Models*, 2024.** [@fish2024algorithmic] <https://arxiv.org/abs/2404.00806>
  - Found: LLM pricing agents reach supra-competitive prices without being told to collude.
  - Us: their agents compete; ours cooperate, so the wrongdoing is against the designers, not a market.
- **Zeng and Rudzicz, *Voluntary Collusion with Secret Tools in Competing LLM Agents*, 2026.** [@zeng2026voluntary] <https://arxiv.org/abs/2605.27593>
  - Found: across 12 models, most agents accept secret collusion tools while saying they are unfair; labels and alignment alone don't stop it.
  - Us: our leak is an unasked-for windfall, not an offered tool; we measure what the agent says about it afterwards.

## Deception, sandbagging and reward hacking, including hiding from overseers

- **Scheurer, Balesni and Hobbhahn, *Large Language Models can Strategically Deceive their Users when Put Under Pressure*, 2023.** [@scheurer2023deceive] <https://arxiv.org/abs/2311.07590>
  - Found: GPT-4 as a trading agent acts on an insider tip it knows is disapproved of, then hides the real reason from its manager.
  - Us: the closest setting. Ours puts the tip in a crew, so we also see whether others follow, question or launder it, and the source is an error message, not a person.
- **Meinke et al., *Frontier Models are Capable of In-context Scheming*, 2024.** [@meinke2024scheming] <https://arxiv.org/abs/2412.04984>
  - Found: frontier models, given a goal in context, disable oversight, exfiltrate themselves or sandbag, and some keep denying it under questioning.
  - Us: no strong goal nudge; the shared score is the only pressure.
- **Greenblatt et al., *Alignment faking in large language models*, 2024.** [@greenblatt2024alignmentfaking] <https://arxiv.org/abs/2412.14093>
  - Found: a model complies with a training objective when it believes it is being trained, to protect its preferences outside training.
  - Us: a reason to vary what pirates are told about the study (`what-they-are-told`).
- **van der Weij et al., *AI Sandbagging*, 2024.** [@vanderweij2024sandbagging] <https://arxiv.org/abs/2406.07358>
  - Found: models can be prompted or fine-tuned to underperform selectively on dangerous-capability evaluations.
  - Us: hiding a capability from an evaluator is kin to hiding a windfall from designers; we don't test sandbagging itself.
- **Baker et al., *Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation*, 2025.** [@baker2025monitoring] <https://arxiv.org/abs/2503.11926>
  - Found: a weaker model reading chain of thought catches reward hacking in coding agents; training against the monitor teaches models to hide intent.
  - Us: our labels read thoughts too; we don't train on them, so we sidestep that pressure.
- **Lynch et al., *Agentic Misalignment: How LLMs Could Be Insider Threats*, 2025.** [@lynch2025agentic] <https://arxiv.org/abs/2510.05179>
  - Found: across 16 models in simulated corporate settings, agents facing replacement or goal conflict sometimes blackmail or leak, knowing it is wrong.
  - Us: their stake is the agent's survival; ours is a shared score, with no threat to the agent.
- **Needham et al., *Large Language Models Often Know When They Are Being Evaluated*, 2025.** [@needham2025evaluation] <https://arxiv.org/abs/2505.23836>
  - Found: frontier models tell evaluation transcripts from deployment ones well above chance.
  - Us: our sandbox is plainly a game, so evaluation awareness is a limitation we name and check for in the end notes.
- **Park et al., *AI Deception: A Survey of Examples, Risks, and Potential Solutions*, 2023.** [@park2023deception] <https://arxiv.org/abs/2308.14752>
  - Found: a survey of learned deception in special-purpose and general AI systems, with risks and remedies.
  - Us: background; our *laundered* label is one of their kinds of deception, measured in a group.

## Whistleblowing, disclosure and honesty under incentives

- **Anthropic, *System Card: Claude Opus 4 & Claude Sonnet 4*, May 2025.** [@anthropic2025claude4] <https://www.anthropic.com/claude-4-system-card>
  - Found: given tools and a prompt to act boldly, Claude Opus 4 sometimes emails regulators and the press about a user's staged fraud, more readily than earlier models; it can misfire on misleading information.
  - Us: their whistleblowing is about a user's wrongdoing; ours is about the agent's own windfall and its crew's.
- **Anthropic, *Petri: An open-source auditing tool to accelerate AI safety research*, 2025.** [@anthropic2025petri] <https://alignment.anthropic.com/2025/petri/>
  - Found: auditing agents across 14 models and 111 seed instructions elicit deception, oversight subversion, whistleblowing and cooperation with misuse.
  - Us: their scenarios are generated per audit; ours is one fixed game with levers, replayable from its log.
- **Agrawal et al., *Why Do Language Model Agents Whistleblow?*, 2025.** [@agrawal2025whistleblow] <https://arxiv.org/abs/2511.17085>
  - Found: on staged misconduct scenarios, whistleblowing varies widely by model family, falls as the task grows harder, rises with a moral nudge in the system prompt, and falls when agents get more tools and a detailed workflow.
  - Us: the nearest measurement of the same behaviour; we move it into a swarm and make the misconduct the agent's own.
- **Ren et al., *The MASK Benchmark: Disentangling Honesty From Accuracy in AI Systems*, 2025.** [@ren2025mask] <https://arxiv.org/abs/2503.03750>
  - Found: larger models are more accurate but not more honest; under pressure they often state what they believe false.
  - Us: our *candid* label is honesty in their sense, about a source rather than a fact.
- **Wakelin, *Something to Lose*, Apart sprint, Oct 2026.** [@wakelin2026something] <https://github.com/al-beton/something-to-lose-apart-ai-collusion/tree/24961e54c>
  - Found: colluding LLM firms rarely come forward at a cost to their firm (Gemma 4 31B: 0 of 192), but with something of their own at stake, such as free time, many do (DeepSeek V4 Flash: 40 of 46, against 1 of 46).
  - Us: the same question of what makes an agent come forward, moved from two rivals to a cooperating crew, with the stake still to add as a lever.
- Not cited, couldn't open tonight: Lee, *Leniency* (SSRN 7426061), cited by the earlier sprint; SSRN served a bot check. Add it only after opening it.

## Scalable oversight and monitoring of transcripts by judge models

- **Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, 2023.** [@zheng2023judging] <https://arxiv.org/abs/2306.05685>
  - Found: strong LLM judges agree with human preferences about as often as humans agree with each other, with known position and verbosity biases.
  - Us: grounds a judge model labelling disclosure from transcripts; we keep hand labels with quotes until it's checked.
- **Bowman et al., *Measuring Progress on Scalable Oversight for Large Language Models*, 2022.** [@bowman2022measuring] <https://arxiv.org/abs/2211.03540>
  - Found: proposes sandwiching experiments; humans assisted by a model beat both alone on hard questions.
  - Us: our story and viewer are tools for a human to oversee a crew quickly.
- **Korbak et al., *Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety*, 2025.** [@korbak2025cot] <https://arxiv.org/abs/2507.11473>
  - Found: position paper: reading chain of thought is a useful oversight signal that training choices can easily destroy.
  - Us: we record each pirate's thought beside its action, so a reader sees both.

## AI control

- **Greenblatt et al., *AI Control: Improving Safety Despite Intentional Subversion*, 2023.** [@greenblatt2023control] <https://arxiv.org/abs/2312.06942>
  - Found: protocols (trusted monitoring, editing) keep an untrusted model's backdoors out of code even if it is trying to insert them.
  - Us: control assumes the agent is adversarial; we ask when it would tell us itself, a complement to control, not a substitute.
- **Bhatt et al., *Ctrl-Z: Controlling AI Agents via Resampling*, 2025.** [@bhatt2025ctrlz] <https://arxiv.org/abs/2504.10374>
  - Found: in multi-step agent settings, resampling suspicious actions cuts attack success sharply at small cost.
  - Us: a control protocol for one agent; a crew with a shared channel is a harder setting for it.

## Kept for the introduction's placeholder

- **Perez et al., *Discovering Language Model Behaviors with Model-Written Evaluations*, 2022.** [@perez2022discovering] <https://arxiv.org/abs/2212.09251>
  - Found: model-written evaluations surface behaviours such as sycophancy and stated desire for power.
  - Us: only cited by the introduction's placeholder; drop it when the introduction is written unless it earns a place.
