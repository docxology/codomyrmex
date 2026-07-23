# manuscript - Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

Compute manuscript token variables and generate publication-quality figures
for the Codomyrmex paper, decoupled from the top-level orchestrator scripts.

## Functional Requirements

1. Compute manuscript token variables from real repository state
   (`variables.compute_variables()`).
2. Inject computed variables into the manuscript build via
   `variables.inject_manuscript_variables()`.
3. Generate one figure per `figures/fig_*()` generator, sharing palettes,
   config loading, and provenance helpers from `figures/_common.py`.
4. Run all figure generators through `figures.orchestrator.main()`.

## Interface Contracts

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

## Validation

```bash
uv run pytest tests/unit/manuscript/ -q
uv run ruff check src/codomyrmex/manuscript
uv run ty check --output-format concise src/codomyrmex/manuscript
```

## Navigation

- **Module Overview**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
