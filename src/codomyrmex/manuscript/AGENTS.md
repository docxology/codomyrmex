# AGENTS.md — `codomyrmex.manuscript`

## Purpose

Manuscript token computation and publication figure generation.

## Key Files

| Module | Role |
| --- | --- |
| `variables.py` | `compute_variables()`, `inject_via_infrastructure()` — token provenance |
| `figures/_common.py` | Palettes, config loaders, `_save`, provenance helpers |
| `figures/*.py` | One module per figure (`cover.py`, `pressure_loop.py`, …) |
| `figures/orchestrator.py` | `main()` — runs all generators |
| `figures/__init__.py` | `FIGURES` registry + re-exports |
| `figures/generators.py` | Backward-compat re-export shim |

## Dependencies

Orchestrators (thin):

- `scripts/z_generate_manuscript_variables.py` → `codomyrmex.manuscript.variables`
- `scripts/generate_manuscript_figures.py` → `codomyrmex.manuscript.figures.main`

Backward-compat shim: `src/manuscript_variables.py` re-exports `codomyrmex.manuscript.variables`.

## Development Guidelines

- Keep `figures/*.py` one-generator-per-file; shared styling lives in `figures/_common.py` only.
- Preserve the `variables.py` / `figures.main()` public entry points — the top-level shims depend on them.
- Regenerate variables and figures together (`compute_variables()` then `figures.main()`) so tokens and figures stay in sync.
