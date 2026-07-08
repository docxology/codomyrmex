# manuscript - Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Compute manuscript token variables and generate publication-quality figures
for the Codomyrmex paper, decoupled from the top-level orchestrator scripts.

## Functional Requirements

1. Compute manuscript token variables from real repository state
   (`variables.compute_variables()`).
2. Inject computed variables into the manuscript build via
   `variables.inject_via_infrastructure()`.
3. Generate one figure per `figures/fig_*()` generator, sharing palettes,
   config loading, and provenance helpers from `figures/_common.py`.
4. Run all figure generators through `figures.orchestrator.main()`.

## Interface Contracts

```python
from codomyrmex.manuscript.variables import compute_variables, inject_via_infrastructure
from codomyrmex.manuscript.figures import main as generate_all_figures

variables = compute_variables()
inject_via_infrastructure(variables)
generate_all_figures()
```

## Validation

```bash
uv run pytest tests/unit/manuscript/ -q
uv run ruff check src/codomyrmex/manuscript
uv run ty check --output-format concise src/codomyrmex/manuscript
```

## Navigation

- **Module Overview**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
