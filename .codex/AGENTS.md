# AGENTS.md — `codomyrmex/.codex`

## Purpose
Configuration for the Codex agent runtime: `config.toml` runtime settings plus
documentation pair.

## Layout
- `config.toml` — Codex runtime configuration (model, approval, sandbox settings).

## Gotchas
- Do not commit secrets or credentials into `config.toml`; keep secrets in the
  runtime's own credential store.
- Treat edits as behavior changes for any Codex-driven agent sessions.

## Key Files
- `README.md`: Readme file

## Dependencies
- None

## Development Guidelines
- Follow standard practices
