# AGENTS.md — `codomyrmex/data`

## Purpose

Repository-level data area for committed evidence that code and docs reference
by path. It currently hosts only the archived SAIR Mathematics Distillation run
records and results.

## Key Files

- [`sair/`](sair/README.md) — SAIR data: `runs/` (three archived 2026-03-16 run
  JSONs) and `results/` (`initial_test.json`).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Written and read by the SAIR tooling in [`scripts/sair/`](../scripts/sair/README.md)
  (`run_sair.py`, `evaluate.py`, `analyze_results.py`); see
  [sair/AGENTS.md](sair/AGENTS.md) for which paths are defaults and which must
  be passed explicitly.
- No code under `src/codomyrmex/` reads from this directory.
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Run JSONs are generated evidence — do not hand-edit; regenerate through the
  SAIR pipeline (`scripts/sair/`).
- Large/bulk data belongs in `data/` only when referenced by deterministic code;
  transient artifacts belong in `output/` (git-ignored at every depth).
- The SAIR problem sets (`normal.jsonl`, `hard.jsonl`) are not committed;
  `scripts/sair/download_data.py` fetches them from Hugging Face only when live
  mode is enabled (`--live` or `RUN_LIVE_SAIR=1`).
- Give any new subdirectory its own `README.md` and `AGENTS.md`, matching the
  existing `sair/` tree.
