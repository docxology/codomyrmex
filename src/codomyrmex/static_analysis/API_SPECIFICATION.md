# Static Analysis Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `static_analysis` module provides AST-based code analysis for import scanning, architectural layer-boundary violation detection, export auditing, dead code detection, and unused function detection. It operates on Python source files without executing them.

This module exposes only a Python import API — it has no MCP tools. See `MCP_TOOL_SPECIFICATION.md`.

## 2. Core Components

### 2.1 Import Analysis (`imports.py`)

**Layer Constants**: Four sets define the architectural hierarchy (from `SPEC.md`):
- `FOUNDATION`: `config_management`, `environment_setup`, `logging_monitoring`, `model_context_protocol`, `telemetry`, `terminal_interface`
- `CORE`: `cache`, `coding`, `git_operations`, `llm`, `performance`, `search`, `static_analysis`, and others
- `SERVICE`: `api`, `auth`, `ci_cd_automation`, `cloud`, `orchestrator`, and others
- `SPECIALIZED`: `agentic_memory`, `agents`, `cerebrum`, `cli`, `events`, and all remaining modules

**Functions**:

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_layer` | `(module: str) -> str` | `"foundation" \| "core" \| "service" \| "specialized" \| "other"` | Classify a module by architectural layer |
| `extract_imports_ast` | `(filepath: Path) -> List[str]` | `List[str]` | Extract imported codomyrmex module names from a single file using AST |
| `scan_imports` | `(src_dir: Path) -> List[Dict[str, Any]]` | `List[edge dicts]` | Scan all `.py` files; each edge has `src`, `dst`, `file`, `src_layer`, `dst_layer` |
| `check_layer_violations` | `(edges: List[Dict]) -> List[Dict]` | `List[violation dicts]` | Apply layer rules; violations add a `reason` field |

**Layer violation rules** (lower-ranked layers cannot import higher-ranked):
- Foundation (0) must not import Core (1), Service (2), or Specialized (3)
- Core (1) must not import Service (2) or Specialized (3)
- Service (2) must not import Specialized (3)

### 2.2 Export Analysis (`exports.py`)

**Functions**:

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_modules` | `(src_dir: Path) -> list[Path]` | `list[Path]` | Return module dirs that have `__init__.py` |
| `check_all_defined` | `(init_path: Path) -> tuple[bool, list[str] \| None]` | `(has_all, names)` | Parse `__init__.py` for `__all__` definition |
| `audit_exports` | `(src_dir: Path) -> list[dict]` | Findings with `module`, `issue`, `detail` | Find modules missing `__all__` |
| `find_dead_exports` | `(src_dir: Path) -> list[dict]` | Findings with `module`, `export_name`, `detail` | Find `__all__` exports never imported elsewhere |
| `find_unused_functions` | `(src_dir: Path) -> list[dict]` | Findings with `file`, `function_name`, `detail` | Find top-level public functions never referenced |
| `full_audit` | `(src_dir: Path) -> dict[str, Any]` | `{missing_all, dead_exports, unused_functions, summary}` | Run all audits; summary has counts |

## 3. Usage Example

```python
from pathlib import Path
from codomyrmex.static_analysis.imports import scan_imports, check_layer_violations
from codomyrmex.static_analysis.exports import full_audit

src = Path("src/codomyrmex")

# Check for architectural violations
edges = scan_imports(src)
violations = check_layer_violations(edges)
for v in violations:
    print(f"VIOLATION: {v['reason']} in {v['file']}")

# Full export audit
report = full_audit(src)
print(f"Modules missing __all__: {report['summary']['modules_missing_all']}")
print(f"Dead exports: {report['summary']['dead_export_count']}")
print(f"Unused functions: {report['summary']['unused_function_count']}")
```
