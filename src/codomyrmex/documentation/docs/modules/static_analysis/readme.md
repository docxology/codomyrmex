# static_analysis

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Static analysis utilities for auditing Python module exports and imports. The top-level `static_analysis` module focuses on `__all__` definition auditing, dead export detection, and import layer violation checking. A separate `coding/static_analysis` sub-package handles linter integration (pylint, flake8, pyrefly) and is documented under the `coding` module.

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| VERIFY | Audit `__all__` definitions, detect dead exports, check layer violations |
| OBSERVE | Full audit report with summary counts |

## Key Exports

From `src/codomyrmex/static_analysis/`:

- **`scan_imports(path)`** -- Scan a directory for all import statements
- **`check_layer_violations(path)`** -- Detect import violations across architectural layers
- **`extract_imports_ast(path)`** -- AST-based import extraction from a single file
- **`audit_exports(path)`** -- Audit modules for missing `__all__` definitions
- **`check_all_defined(path)`** -- Check whether `__all__` is properly defined

From `src/codomyrmex/coding/static_analysis/`:

- **`StaticAnalyzer`** -- Main analyzer class for multi-tool analysis
- **`analyze_file(path)`** -- Analyze a single file
- **`analyze_project(paths)`** -- Analyze an entire project
- **`get_available_tools()`** -- List available analysis tools
- **`PyreflyRunner`** -- Pyrefly integration for type checking

## MCP Tools

| Tool | Description |
|------|-------------|
| `static_analysis_audit_exports` | Audit modules for missing `__all__` definitions |
| `static_analysis_find_dead_exports` | Find `__all__` entries never imported elsewhere |
| `static_analysis_full_audit` | Run all static analysis audits with summary counts |

## Quick Start

```python
from codomyrmex.static_analysis import audit_exports, check_layer_violations
from pathlib import Path

findings = audit_exports(Path("src/codomyrmex"))
violations = check_layer_violations(Path("src/codomyrmex"))
```

## Architecture

```
static_analysis/          (top-level module)
  __init__.py             -- Exports scan_imports, audit_exports, etc.
  exports.py              -- audit_exports, find_dead_exports, full_audit
  imports.py              -- scan_imports, check_layer_violations, extract_imports_ast
  mcp_tools.py            -- 3 MCP tool definitions

coding/static_analysis/   (sub-package within coding)
  __init__.py             -- StaticAnalyzer, models, pyrefly, tool runners
  static_analyzer.py      -- Main analyzer class
  pyrefly_runner.py       -- Pyrefly integration
  tool_runners.py         -- External tool subprocess execution
  models.py               -- AnalysisResult, AnalysisSummary, etc.
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/static_analysis/ -v
```

## Navigation

- [Root](../../../../../../README.md)
