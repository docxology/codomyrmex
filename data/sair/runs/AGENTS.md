# AGENTS.md — `codomyrmex/data/sair/runs`

## Purpose
Timestamped SAIR distillation run records. Each JSON carries a `summary` block
(run id, correlation id, model, dataset, cheatsheet hash, timestamps) plus
per-item results.

## Gotchas
- Append-only evidence: never modify or rename existing run files.
- Correlation IDs tie runs to logs/telemetry — preserve them when archiving.

## Key Files
- `README.md`: Readme file

## Dependencies
- None

## Development Guidelines
- Follow standard practices
