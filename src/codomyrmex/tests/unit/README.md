# Unit tests (`src/codomyrmex/tests/unit`)

**Last updated**: April 2026

## Overview

Tests for the `codomyrmex` package. Policy and gates: **[SPEC.md](SPEC.md)**. Layout and fixtures: **[AGENTS.md](AGENTS.md)**.

This folder contains many per-module subtrees (`<module>/` mirrors `codomyrmex.<module>`). The auto-generated flat file listing is intentionally omitted here; discover tests with `find` or your editor’s tree, or run pytest with a path prefix.

## Running

From the repository root:

```bash
# Entire unit tree (slow; may require optional services locally)
uv run pytest src/codomyrmex/tests/unit/ -q

# Single module
uv run pytest src/codomyrmex/tests/unit/cloud/ -q

# Coverage gate (40% minimum in `pyproject.toml` / CI)
uv run pytest src/codomyrmex/tests/unit/ --cov=src/codomyrmex --cov-fail-under=40 -q
```

Full local runs can fail when optional backends (Ollama, Docker, vector DBs, live API tokens) are missing or misconfigured. **CI with declared extras is the usual release gate.** Use narrow `pytest …/path/` loops while developing.

## Hermes

- **`hermes/`** — client, session, templates, gateway, monitoring, provider router, plugins, MCP extended tools.
- **`agents/hermes/`** — MCP Hermes tool entrypoints.
- **`agents/test_agents_hermes_client.py`** — CLI argument construction and execution paths for `HermesClient`.

## Shared fixtures

**`conftest.py`**: `src_root`, `project_root`, minimal git/project fixtures, Ollama/registry URL helpers, Docker/Ollama skip markers.

## Navigation

- [SPEC.md](SPEC.md) · [AGENTS.md](AGENTS.md) · [Parent `tests/`](../README.md) · [Repository root](../../../../README.md)
