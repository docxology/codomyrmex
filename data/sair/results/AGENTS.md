# AGENTS.md — `codomyrmex/data/sair/results`

## Purpose

Aggregated SAIR result artifacts (currently `initial_test.json`): early
evaluation outputs kept for reference alongside the full run records in
`../runs/`.

## Key Files

- `initial_test.json` — first verification batch: `normal_0001`–`normal_0003`
  on `gemini-2.5-flash` without a cheatsheet, 0/3 correct. It predates the run
  telemetry schema: `summary` holds only `accuracy`, `correct`, `total`,
  `model`, and `cheatsheet_path`, and each result only `problem_id`, `parsed`,
  `raw_response`, `is_correct`, `latency`, and `usage` (no `run_id`,
  `ground_truth`, or timestamps).
- [`README.md`](README.md) — human signpost.

## Dependencies

- [`scripts/sair/analyze_results.py`](../../../scripts/sair/analyze_results.py)
  `--run-file` still reads it, reporting `run_id=unknown` and dataset `unknown`.
- Full-schema runs live in [`../runs/`](../runs/AGENTS.md); the generating
  tooling is documented in [scripts/sair/AGENTS.md](../../../scripts/sair/AGENTS.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Archival LLM output cannot be reproduced exactly; do not hand-edit or
  re-generate it in place — write a new file under a new name instead.
- Do not upgrade `initial_test.json` to the run schema by inventing fields it
  never recorded (for example `ground_truth` or timestamps).
- New full-schema evaluations belong in `../runs/`; reserve this folder for
  aggregate or summary outputs.
