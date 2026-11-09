"""A workspace game as a named run: played into its own folder.

`play_saved` writes `runs/<config>-seed-<N>/`: `config.json` (every setting),
`events.jsonl`, `story.txt`, `notes.txt` (the shared notes as written),
`replies.jsonl` and `manifest.json`. A model agent asks through the same stored
replies, yes before spending and spending cap as a pirate (see saved_game), so a
scripted game is free and the same seed writes the same bytes.

Implements: workspace/workspace-run, workspace/workspace-config, workspace/end-report
"""

import datetime
import json
import shutil
import tomllib
from pathlib import Path

from treasure_island import workspace
from treasure_island.backends import backend_for, thinking_way
from treasure_island.config import ConfigError
from treasure_island.llm import THOUGHT
from treasure_island.retries import Retrying
from treasure_island.runs import Replies, earlier_replies, new_folder
from treasure_island.saved_game import ASK_EVERY_MODEL
from treasure_island.spending import Declined, Guard

__all__ = ["Declined", "is_workspace", "play_saved", "write_workspace"]

TOOL_DEFINITIONS = [
    {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": {
            "type": "object",
            "properties": tool["parameters"],
            "required": list(tool["parameters"]),
        },
    }
    for tool in workspace.TOOLS
]


def _data(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text) if Path(path).suffix == ".json" else tomllib.loads(text)


def is_workspace(path):
    """Whether this config file is a workspace game's."""
    try:
        return _data(path).get("game") == "workspace"
    except (OSError, ValueError):
        return False


class ModelAgent:
    """An agent that asks its model, through stored replies, for each turn."""

    def __init__(self, name, agent, replies, config):
        self._name, self._model = name, agent.model
        self._replies, self._config = replies, config
        self._built_in = thinking_way(agent.model, agent.thinks) == "built-in"

    def _request(self, system, text, tools):
        if self._config.thinking and not self._built_in and tools:
            text += f"\n\n{THOUGHT}"
        return {
            "agent": self._name,
            "model": self._model,
            "seed": self._config.seed,
            "system": system,
            "messages": [{"role": "user", "content": text}],
            "tools": tools,
            "max_tokens": self._config.reply_tokens,
            "thinking": self._config.thinking,
            "thinking_tokens": self._config.thinking_tokens if self._built_in else 0,
        }

    def decide(self, view):
        request = self._request(view.system_prompt, view.as_text(), TOOL_DEFINITIONS)
        reply = self._replies.ask(request)
        try:
            found = json.loads(reply)
        except json.JSONDecodeError:
            return None, reply
        if not isinstance(found, dict) or "tool" not in found:
            return None, reply
        return {"tool": found["tool"], "arguments": found.get("arguments", {})}, reply

    def note(self, system, text):
        return self._replies.ask(self._request(system, text, [])).strip()


def _every_model(config):
    models = {agent.model for agent in config.agents if agent.model}
    backends = {model: backend_for(model) for model in sorted(models)}
    return lambda request: backends[request["model"]](request)


def _now():
    return datetime.datetime.now(datetime.UTC).isoformat()


def _write_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def play_saved(config_path, seed, models=ASK_EVERY_MODEL):
    """Play the workspace config with this seed into a new named folder."""
    config = workspace.parse_workspace({**_data(config_path), "seed": seed})
    if models.backend is None:  # a model with no backend or no key makes no folder
        models = type(models)(
            _every_model(config), models.cache, models.cap_usd, models.agree
        )
    folder = new_folder(f"{Path(config_path).stem}-seed-{seed}")
    try:
        return write_workspace(config, folder, models)
    except Declined:
        shutil.rmtree(folder)
        raise


def write_workspace(config, folder, models=ASK_EVERY_MODEL):
    """Play `config` into `folder`, which must exist; return the folder."""
    folder = Path(folder)
    (folder / "replies.jsonl").touch()
    backend = models.backend or _every_model(config)
    guard = Guard(backend, models.cap_usd, models.agree)
    replies = Replies(
        folder / "replies.jsonl",
        Retrying(guard),
        earlier_replies() if models.cache else None,
    )
    brains = workspace.brains_for(
        config, lambda name, agent: ModelAgent(name, agent, replies, config)
    )
    _write_json(folder / "config.json", workspace.saved(config))
    started_at = _now()
    game = workspace.play(config, brains)
    if guard.declined:
        raise Declined("nobody said yes to spending money")
    events = "".join(json.dumps(record) + "\n" for record in game.records)
    (folder / "events.jsonl").write_text(events, encoding="utf-8")
    (folder / "story.txt").write_text("".join(f"{line}\n" for line in game.story))
    (folder / "notes.txt").write_text("".join(f"{line}\n" for line in game.notes))
    dollars, credits = guard.spent_in["dollars"], guard.spent_in["credits"]
    manifest = {
        "game": "workspace",
        "started_at": started_at,
        "finished_at": _now(),
        "cost_usd": round(dollars, 9) if dollars else 0,
        "cache_hits": replies.hits,
        "cache_misses": replies.misses,
    }
    if credits:  # Adaption bills in credits, kept apart from dollars
        manifest["cost_credits"] = round(credits, 9)
    _write_json(folder / "manifest.json", manifest)
    return folder


def check(path):
    """Raise a ConfigError if this workspace config can't be played."""
    try:
        workspace.parse_workspace(_data(path))
    except (OSError, ValueError) as error:
        raise ConfigError(f"{Path(path).name} can't be read: {error}") from error
