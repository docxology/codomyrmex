# manuscript

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The manuscript module computes manuscript token variables from real
repository state and generates the publication-quality figures used in the
Codomyrmex paper. It replaces the former `src/manuscript_variables.py` and
`scripts/generate_manuscript_figures.py` monoliths with a tested package.

## Key Components

| Component | File | Purpose |
| :--- | :--- | :--- |
| `compute_variables()` | `variables.py` | Compute manuscript token variables from repo state |
| `inject_via_infrastructure()` | `variables.py` | Inject computed variables into the manuscript build |
| `figures.main()` | `figures/orchestrator.py` | Run every figure generator |
| `FIGURES` registry | `figures/__init__.py` | Registry of `fig_*()` generators |

## Quick Start

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

- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
