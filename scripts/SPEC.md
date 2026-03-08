# Script Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

> [!IMPORTANT]
> Scripts are **thin orchestrators only**. All business logic lives in `src/codomyrmex/`.

## Architecture

```mermaid
graph TD
    subgraph "Entry Points (scripts/)"
        RAS["run_all_scripts.py"]
        MO["module/orchestrate.py"]
        DASH["pai/dashboard.py"]
    end

    subgraph "Business Logic (src/codomyrmex/)"
        MAIN["orchestrator.core.main()"]
        DISC["system_discovery.discover_scripts()"]
        RUN["orchestrator.runner.run_script()"]
        REP["orchestrator.reporting.generate_report()"]
        PM["agents.pai.pm.server"]
        SK["skills.skill_generator"]
    end

    RAS -->|"import & call"| MAIN
    MO -->|"import & call"| MAIN
    DASH -->|"import & call"| PM
    MAIN --> DISC
    DISC --> RUN
    RUN --> REP

    style RAS fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
    style MO fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
    style DASH fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
    style MAIN fill:#0f3460,stroke:#533483,color:#e8e8e8
    style PM fill:#0f3460,stroke:#533483,color:#e8e8e8
    style SK fill:#0f3460,stroke:#533483,color:#e8e8e8
```

## Directory Structure

The `scripts/` directory mirrors the structure of `src/codomyrmex/`. Each script is a **thin wrapper** that imports from its corresponding `src/codomyrmex/` module.

```
scripts/
├── <module_name>/
│   ├── orchestrate.py  # Thin orchestrator (≤50 lines)
│   └── examples/
│       ├── basic_usage.py
│       └── advanced_workflow.py
├── run_all_scripts.py  # Master orchestrator
└── ...
```

## Thin Orchestrator Pattern

All `orchestrate.py` files follow a consistent pattern — **zero business logic**:

```python
#!/usr/bin/env python3
"""Thin orchestrator for <module_name>."""

import sys
from pathlib import Path

# Ensure codomyrmex is importable
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.<module>.core import main  # Logic lives in src/

if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    if not any(arg.startswith("--scripts-dir") for arg in sys.argv):
        sys.argv.append(f"--scripts-dir={current_dir}")
    sys.exit(main())
```

## What Goes Where

| In `scripts/` | In `src/codomyrmex/` |
|---------------|---------------------|
| CLI entry points | Business logic |
| `sys.path` setup | Data models |
| Arg parsing | API implementations |
| Config loading | Server code |
| Launch commands | Route handlers |

## Naming Conventions

- **Orchestrators**: MUST be named `orchestrate.py`
- **Examples**: Descriptive names (e.g., `basic_usage.py`, `integration_test.py`)
- **Directories**: MUST match the `src/codomyrmex` module name exactly

## Execution Flow

1. **Discovery**: `discover_scripts()` finds all `.py` files in target directory
2. **Environment**: Scripts set up `sys.path` to import `codomyrmex`
3. **Execution**: `run_script()` runs each script with timeout
4. **Reporting**: `generate_report()` creates summary JSON

## CLI Options

```bash
python run_all_scripts.py [options]

Options:
  --dry-run, -n        List scripts without executing
  --timeout, -t SEC    Timeout per script (default: 60)
  --subdirs, -s DIRS   Filter by subdirectory names
  --filter, -f PAT     Filter scripts by name pattern
  --output-dir, -o     Output directory for logs
  --verbose, -v        Show detailed output
  --max-depth N        Maximum search depth (default: 2)
  --generate-docs FILE Generate Markdown documentation
```

## Navigation

- [README.md](README.md) | [PAI.md](PAI.md) | [AGENTS.md](AGENTS.md)
- [Source Code](../src/codomyrmex/) | [Project Root](../README.md)
