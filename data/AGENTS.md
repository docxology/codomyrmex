# AGENTS.md — `codomyrmex/data`

## Purpose
Repository-level data area. Currently hosts the SAIR distillation outputs only.

## Layout
- `sair/` — SAIR Mathematics Distillation run data: `runs/` (timestamped run JSONs) and `results/` (aggregate results).

## Gotchas
- Run JSONs are generated evidence — do not hand-edit; regenerate through the SAIR
  pipeline (`scripts/sair/`).
- Large/bulk data belongs in `data/` only when referenced by deterministic code;
  transient artifacts belong in `output/`.
