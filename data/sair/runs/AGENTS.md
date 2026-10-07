# AGENTS.md — `codomyrmex/data/sair/runs`

## Purpose

Timestamped SAIR distillation run records. Each JSON carries a `summary` block
(run id, correlation id, model, dataset, cheatsheet hash, timestamps) plus
per-item results.

## Key Files

- `run_20260316T060942_61ab1529.json` — 5 problems from `normal.jsonl`, no
  cheatsheet (baseline); 0/5 correct.
- `run_20260316T063521_0c85d70d.json` — 5 problems from `hard.jsonl` with
  `cheatsheets/full_v2.txt`; 1/5 correct.
- `run_20260316T065031_10b79af4.json` — 2 problems from `hard.jsonl` with the
  same cheatsheet; 1/2 correct; the first archived run whose results include
  `confidence` and `log_loss`.
- [`README.md`](README.md) — human signpost.

All three used `gemini-2.5-flash`. Each `results` entry records `problem_id`,
`equation1`, `equation2`, `ground_truth`, `verdict`, `is_correct`, the parsed
and raw model response, `latency`, `attempts`, `usage`, and `memory_delta_mb`.

## Dependencies

- Produced by `run_evaluation()` in [`scripts/sair/evaluate.py`](../../../scripts/sair/evaluate.py)
  (via `run_sair.py evaluate --runs-dir data/sair/runs`).
- Read by [`scripts/sair/analyze_results.py`](../../../scripts/sair/analyze_results.py)
  and by `run_sair.py generate --refine-from <run>.json` to refine a cheatsheet.
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Append-only evidence: never modify or rename existing run files.
- Correlation IDs tie runs to logs/telemetry — preserve them when archiving.
- The filename timestamp comes from `format_timestamp()` in
  `scripts/sair/utils.py`: naive local time when the run was saved (its end),
  not UTC start. Order or compare runs by `summary.timestamp_start` and
  `summary.timestamp_end`, which are UTC.
- Cheatsheet refinement (`refine_from_results()` in
  `scripts/sair/generate_cheatsheet.py`) reads `summary.run_id` and each
  result's `is_correct`, `ground_truth`, `problem_id`, `equation1`, and
  `equation2`; an archived run must keep those fields intact.
