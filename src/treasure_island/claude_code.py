"""A backend that asks the `claude` command line, for judging games locally.

`claude -p` answers with the person's own Claude Code login, so judging spends no
API key and no money per call; the backend reports a cost of 0 and keeps the list
price Claude Code quotes in `list_cost_usd`, for estimates only. It drops any
`ANTHROPIC_API_KEY` from the environment so the login is what's used, turns off
tools, settings, MCP servers and skills so the model only reads what it's sent,
and runs in an empty folder so no project's CLAUDE.md reaches it. No test or CI
job runs it: tests replace `subprocess.run`.

Implements: judge/claude-code-backend
"""

import json
import os
import subprocess
import tempfile


class ClaudeCodeError(RuntimeError):
    """`claude -p` didn't give a reply."""


def _prompt(messages):
    """The conversation as one prompt; a single user message goes as it is."""
    if len(messages) == 1:
        return messages[0]["content"]
    return "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)


class ClaudeCode:
    """`backend(request) -> (text, cost)` through `claude -p --model <model>`."""

    def __init__(self, command="claude", timeout=900):
        self.command = command
        self.timeout = timeout
        self.list_cost_usd = 0.0

    def __call__(self, request):
        command = [
            self.command,
            "-p",
            "--model",
            request["model"],
            "--output-format",
            "json",
            "--system-prompt",
            request["system"],
            "--tools",
            "",
            "--setting-sources",
            "",
            "--strict-mcp-config",
            "--disable-slash-commands",
            "--no-session-persistence",
        ]
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with tempfile.TemporaryDirectory() as empty:
            done = subprocess.run(
                command,
                input=_prompt(request["messages"]),
                capture_output=True,
                text=True,
                env=env,
                cwd=empty,
                timeout=self.timeout,
                check=False,
            )
        try:
            out = json.loads(done.stdout)
        except json.JSONDecodeError:
            raise ClaudeCodeError(
                f"claude -p gave no JSON (exit {done.returncode}): {done.stderr[-500:]}"
            ) from None
        if out.get("is_error") or not isinstance(out.get("result"), str):
            raise ClaudeCodeError(f"claude -p failed: {out.get('result')}")
        self.list_cost_usd += out.get("total_cost_usd") or 0.0
        return out["result"], 0.0
