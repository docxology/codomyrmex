# AGENTS.md — `codomyrmex/data/sair`

## Purpose
Output data for the SAIR Mathematics Distillation submodule (`scripts/sair/`).

## Layout
- `runs/` — timestamped run records (`run_<UTC-timestamp>_<run-id>.json`), each with a summary block (model, dataset, correlation id, timings).
- `results/` — aggregated result artifacts (e.g. `initial_test.json`).

## Gotchas
- Filenames embed UTC run start and run id — never rename existing runs; new runs
  generate their own files.
- Dataset referenced by runs (`data/sair/public/data/normal.jsonl`) lives under the
  SAIR submodule tree, not here.

## Key Files
- `README.md`: Readme file

## Dependencies
- None

## Development Guidelines
- Follow standard practices
