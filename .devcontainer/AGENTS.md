# AGENTS.md — `codomyrmex/.devcontainer`

## Purpose

Dev Container definition for reproducible VS Code / GitHub Codespaces
environments: a Python 3.11 image with `uv`, `just`, and Node LTS, the
repository's lint and type-check extensions, and forwarded ports for the local
docs and dashboard servers.

## Key Files

- [`devcontainer.json`](devcontainer.json) — the whole definition:
  - `image`: `mcr.microsoft.com/devcontainers/python:3.11`, the
    `requires-python` floor and the pull-request CI interpreter;
  - `features`: `just` and Node LTS;
  - `postCreateCommand`: installs `uv` with the upstream installer, then runs
    `uv sync --all-groups` (dev, docs, lint, and test groups; no optional extras);
  - VS Code settings: Ruff as formatter and fixer from `.venv/bin/ruff`, the
    `ty` extension, interpreter `.venv/bin/python`;
  - `forwardPorts`: 8000 (docs server), 8787 (admin dashboard), 8888 (PAI dashboard);
  - `remoteUser`: `vscode`.
- [`README.md`](README.md) — human signpost.

## Dependencies

- [`pyproject.toml`](../pyproject.toml) — `requires-python` and the
  `[dependency-groups]` that `uv sync --all-groups` installs.
- [`justfile`](../justfile) — recipes available through the `just` feature.
- Port owners: `mkdocs serve` (`make serve-docs` / `just docs-serve`, port 8000),
  `codomyrmex dashboard` (default 8787 in `src/codomyrmex/cli/core.py`), and the
  PAI PM server (`PAI_PM_PORT`, default 8888 in `src/codomyrmex/website/pai_mixin.py`).
- The production image is built separately from [`Dockerfile`](../Dockerfile)
  (Python 3.13, `uv sync --frozen --no-dev`); neither file is derived from the other.
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Keep the image at the supported Python floor unless `requires-python` and the
  CI matrix move with it; drift here produces environments where the test suite
  fails for dependency reasons rather than code reasons.
- Optional module extras are not installed; add them explicitly
  (`uv sync --all-groups --extra <module>`) before running that module's tests.
- When a server's default port changes in code, update `forwardPorts` and
  `portsAttributes` together.
- Keep editor settings aligned with repository tooling (Ruff for format and
  lint, `ty` for type checks); do not add a second formatter.
