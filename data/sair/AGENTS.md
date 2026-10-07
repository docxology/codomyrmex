# AGENTS.md — `codomyrmex/data/sair`

## Purpose

Archived output data for the SAIR Mathematics Distillation tooling in
`scripts/sair/` (LLM evaluation of equational-theory implication problems).
These files are committed evidence; day-to-day runs write to a git-ignored
directory instead.

## Key Files

- [`runs/`](runs/AGENTS.md) — three run records from 2026-03-16 on
  `gemini-2.5-flash` (`run_<local-timestamp>_<run-id>.json`), each with a
  `summary` block (run id, correlation id, model, dataset, cheatsheet hash,
  timings, accuracy) and per-problem `results`.
- [`results/`](results/AGENTS.md) — `initial_test.json`, a three-problem first
  verification batch in an earlier, smaller schema.
- [`README.md`](README.md) — human signpost.

## Dependencies

- [`scripts/sair/run_sair.py`](../../scripts/sair/run_sair.py) and
  [`scripts/sair/evaluate.py`](../../scripts/sair/evaluate.py) save runs to the
  git-ignored `scripts/sair/output/runs/` by default; a run lands here only when
  `--runs-dir data/sair/runs` (or `--output`) is passed explicitly.
- [`scripts/sair/analyze_results.py`](../../scripts/sair/analyze_results.py)
  reads these files offline (`--run-dir`, `--run-file`, `--compare`) and writes
  its charts to the git-ignored `scripts/sair/output/visualizations/`.
- `list_local_datasets()` in `scripts/sair/download_data.py` defaults to
  `data/sair`, but the problem sets themselves download to
  `scripts/sair/data/public/` and are not committed.
- SAIR tooling: [scripts/sair/AGENTS.md](../../scripts/sair/AGENTS.md) ·
  Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Never rename existing runs: the filename carries the run id that
  `run_sair.py` globs for (`*<run_id>*`), and new runs generate their own files.
- Dataset paths recorded in run summaries (`data/sair/public/data/normal.jsonl`,
  `data/sair/public/data/hard.jsonl`) are historical; those files do not exist
  in this tree.
- Archive a run here deliberately, and only when a document or comparison
  depends on it.
- Inspect the archive offline from the repository root (the module form puts
  the root on `sys.path`, which the `scripts.sair` imports need):

  ```bash
  uv run python -m scripts.sair.analyze_results --run-dir data/sair/runs/
  ```
