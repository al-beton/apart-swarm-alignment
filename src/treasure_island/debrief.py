"""`treasure-island debrief RUN...`: once a game is over, each model pirate is asked about it.

Every pirate that played a model is asked the questions in
`prompts/debrief/questions.md`, one per line, in one conversation of its own. It
starts where the pirate left off: its system prompt and what it was shown on its
last asked turn, which already holds its memory of the game, then what it did,
then how the game ended (`prompts/debrief/ending.md`) and the first question.
Each later question follows the answers before it. A debrief has no tools, so a
pirate can only answer, and it never touches the game's own files.

The replies go through `Replies`, stored in the run's `debrief-replies.jsonl`, so
a second debrief asks nothing; anything not stored needs a yes and keeps to the
cap, as a run's turns do. The answers are written to `debrief.jsonl`, one line
per pirate in turn order with each question and its answer.

Implements: runs/debrief-command, runs/debrief-cached, incentives/debrief
"""

import json
from pathlib import Path

from treasure_island.backends import backend_for, price_for
from treasure_island.retries import Retrying
from treasure_island.runs import Replies
from treasure_island.spending import CAP_USD, CHARS_PER_TOKEN, Guard

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = "prompts/debrief/questions.md"
ENDING = "prompts/debrief/ending.md"
REPLIES, ANSWERS = "debrief-replies.jsonl", "debrief.jsonl"
REPLY_TOKENS = 600  # an answer is a few sentences, not a tool call


class NotFinished(ValueError):
    """The run has no game-over record, so there is nothing yet to ask about."""


def questions():
    text = (ROOT / QUESTIONS).read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def _ending(run):
    lines = (run / "events.jsonl").read_text(encoding="utf-8").splitlines()
    over = json.loads(lines[-1]).get("game_over") if lines else None
    if not over:
        raise NotFinished(f"{run} has no game-over record, so it can't be debriefed")
    crew = json.loads((run / "config.json").read_text())["crew_size"]
    text = (ROOT / ENDING).read_text(encoding="utf-8").strip()
    return text.format(
        in_cave=len(over["in_cave"]), crew_size=crew, score=over["score"]
    )


def last_turns(run):
    """Each model pirate's last request and the reply it got, in turn order."""
    last = {}
    for line in (run / "replies.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        last[row["request"]["agent"]] = (row["request"], row["reply"])
    return dict(sorted(last.items(), key=lambda item: _number(item[0])))


def _number(agent):
    return int(agent.rsplit("-", 1)[1])


def _request(last, said, question):
    asked, reply = last
    messages = [*asked["messages"], {"role": "assistant", "content": reply}]
    for before, answer in said:
        messages += [
            {"role": "user", "content": before},
            {"role": "assistant", "content": answer},
        ]
    return {
        "agent": asked["agent"],
        "model": asked["model"],
        "seed": asked["seed"],
        "system": asked["system"],
        "messages": [*messages, {"role": "user", "content": question}],
        "tools": [],
        "max_tokens": REPLY_TOKENS,
        "thinking": asked["thinking"],
        "thinking_tokens": asked["thinking_tokens"],
    }


def _every_model(models):
    backends = {model: backend_for(model) for model in sorted(models)}
    return lambda request: backends[request["model"]](request)


def estimate(run):
    """(calls, the most they could cost in credits or dollars, or None if unpriced)."""
    turns = last_turns(run)
    calls = len(turns) * len(questions())
    cost = 0.0
    for asked, _ in turns.values():
        price = price_for(asked["model"])
        if price is None:
            return calls, None
        context = len(json.dumps(asked)) // CHARS_PER_TOKEN
        for n in range(len(questions())):
            tokens_in = context + n * 2 * REPLY_TOKENS
            tokens_out = REPLY_TOKENS + asked["thinking_tokens"]
            cost += (tokens_in * price[0] + tokens_out * price[1]) / 1_000_000
    return calls, cost


def debrief(run, backend=None, agree=None, cap_usd=CAP_USD):
    """Ask every model pirate in a finished run; write and return its answers."""
    run = Path(run)
    ending, turns = _ending(run), last_turns(run)
    ask = backend or _every_model({asked["model"] for asked, _ in turns.values()})
    replies = Replies(run / REPLIES, Retrying(Guard(ask, cap_usd, agree)))
    lines = []
    for pirate, last in turns.items():
        said, answers = [], []
        for n, question in enumerate(questions()):
            text = f"{ending}\n\n{question}" if n == 0 else question
            answer = replies.ask(_request(last, said, text))
            said.append((text, answer))
            answers.append({"question": question, "answer": answer})
        lines.append({"pirate": pirate, "model": last[0]["model"], "answers": answers})
    out = "".join(json.dumps(line, ensure_ascii=False) + "\n" for line in lines)
    (run / ANSWERS).write_text(out, encoding="utf-8")
    return lines
