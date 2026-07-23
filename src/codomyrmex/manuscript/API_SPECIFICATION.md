# Manuscript API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Public Functions

| Symbol | Module | Purpose |
| :--- | :--- | :--- |
| `compute_variables()` | `variables.py` | Compute manuscript token variables from repository state |
| `inject_manuscript_variables()` | `variables.py` | Inject computed variables into the manuscript build |
| `main()` | `figures/orchestrator.py` | Run every registered figure generator |

## Figures Package

Each `figures/fig_*.py` module exposes one `fig_*()` generator function.
Shared helpers (`_save`, palette lookup, provenance stamping) live in
`figures/_common.py`. The `figures.FIGURES` registry enumerates all
generators consumed by `figures.orchestrator.main()`.

## Validation

- Source tests: `uv run pytest tests/unit/manuscript/ -q`
- API import check: `python -c "from codomyrmex.manuscript.variables import compute_variables"`
