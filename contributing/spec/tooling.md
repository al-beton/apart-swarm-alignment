# Tooling

- **one-command-each:** Installing, linting, testing and checking the spec are each one command.
- **locked-dependencies:** Dependencies are locked, so every machine installs the same versions.
- **how-we-work:** The README gives people the working process in five lines and sends coding agents to `AGENTS.md`.
- **open-license:** The repository is public under the MIT license, so anyone can reuse it.

## Where this is enforced

| Statement | Enforced by | Tested by |
|---|---|---|
| `one-command-each` | `Makefile`, `README.md`, `pyproject.toml` | — |
| `locked-dependencies` | `uv.lock`, `.python-version`, `Makefile` | — |
| `how-we-work` | `README.md` | `test_how_we_work_is_five_lines_and_points_agents_to_agents_md` |
| `open-license` | `LICENSE` | — |
