# manuscript

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

The manuscript module computes manuscript token variables from real repository
state and generates the publication-quality figures used in the Codomyrmex paper.
The package is the single implementation authority; the project-local scripts are
thin command-line entry points.

## Key Components

| Component | File | Purpose |
| :--- | :--- | :--- |
| `compute_variables()` | `variables.py` | Compute manuscript token variables from repo state |
| `inject_manuscript_variables()` | `variables.py` | Inject computed variables into the manuscript build |
| `validate_variable_contract()` | `variables.py` | Detect undefined, unresolved, stale, and unused publication tokens |
| `figures.main()` | `figures/orchestrator.py` | Run every figure generator |
| `FIGURES` registry | `figures/__init__.py` | Registry of `fig_*()` generators |

The generator writes `output/data/manuscript_variables.json` and the
machine-readable `output/data/manuscript_variable_manifest.json`. Every active
prose token, table value, caption, figure annotation, and accessibility string
must resolve from that snapshot or be explicitly classified as mathematical
notation, a citation year, or provenance metadata. The manifest is a contract
check, not evidence that a scientific hypothesis has been supported.

## Quick Start

```python
from pathlib import Path

from codomyrmex.manuscript.variables import (
    compute_variables,
    inject_manuscript_variables,
)
from codomyrmex.manuscript.figures import main as generate_all_figures

project_root = Path.cwd()  # run this example from the repository root
config_path = project_root / "docs/manuscript/config.yaml"
manuscript_dir = project_root / "docs/manuscript"
output_dir = project_root / "output/manuscript"
variables = compute_variables(config_path, project_root)
inject_manuscript_variables(manuscript_dir, output_dir, variables)
generate_all_figures()
```

For a read-only check of an existing snapshot:

```bash
uv run python scripts/validate_manuscript_contract.py
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
