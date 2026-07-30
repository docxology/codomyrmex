# AGENTS.md — `codomyrmex.manuscript`

## Purpose

Manuscript token computation and publication figure generation.

## Key Files

| Module | Role |
| --- | --- |
| `variables.py` | `compute_variables()`, `inject_manuscript_variables()` — token provenance |
| `figures/_common.py` | Palettes, config loaders, `_save`, provenance helpers |
| `figures/*.py` | One module per figure (`cover.py`, `pressure_loop.py`, …) |
| `figures/orchestrator.py` | `main()` — runs all generators |
| `figures/__init__.py` | `FIGURES` registry + re-exports |
| `figures/research_roadmap.py` | Config-driven evidence-roadmap visual |
| `figures/replay_contract.py` | Fixed-input paired-locality evidence visual |

Figure metadata, captions, concise alternatives, and extended descriptions are
configured under `docs/manuscript/config.yaml` in the `figures:` mapping. The generator
resolves those strings into `FIGURE_*` variables, and the figure registry records the
resolved text, label, width, evidence class, and artifact hash together.

## Dependencies

Orchestrators (thin):

- `scripts/z_generate_manuscript_variables.py` → `codomyrmex.manuscript.variables`
- `scripts/generate_manuscript_figures.py` → `codomyrmex.manuscript.figures.main`

## Development Guidelines

- Keep `figures/*.py` one-generator-per-file; shared styling lives in `figures/_common.py` only.
- Preserve the `variables.py` / `figures.main()` public entry points used by the local generation scripts.
- Regenerate variables and figures together (`compute_variables()` then `figures.main()`) so tokens and figures stay in sync.
- Preserve non-colour encodings and keep the palette contrast checks green when
  changing shared figure styling.
