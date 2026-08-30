# AGENTS.md — `codomyrmex/.devcontainer`

## Purpose
Dev Container definition for reproducible codespace environments.

## Layout
- `devcontainer.json` — container image, extensions, and post-create setup.

## Gotchas
- Keep the container feature set in sync with `Dockerfile` and `pyproject.toml`
  extras; drift here produces environments where the test suite fails for
  dependency reasons rather than code reasons.
