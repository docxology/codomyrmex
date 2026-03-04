# static_analysis - Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Static analysis module providing 3 MCP tools for auditing Python module exports and imports. Focuses on `__all__` compliance, dead export detection, and full audit reporting.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Package root; exports `scan_imports`, `audit_exports`, etc. |
| `exports.py` | `audit_exports()`, `find_dead_exports()`, `full_audit()`, `check_all_defined()` |
| `imports.py` | `scan_imports()`, `check_layer_violations()`, `extract_imports_ast()` |
| `mcp_tools.py` | 3 MCP tool definitions |

## MCP Tools Available

| Tool | Parameters | Returns |
|------|-----------|---------|
| `static_analysis_audit_exports` | `src_dir: str` | List of modules missing `__all__` |
| `static_analysis_find_dead_exports` | `src_dir: str` | List of `__all__` entries never imported |
| `static_analysis_full_audit` | `src_dir: str` | Unified report with `missing_all`, `dead_exports`, `unused_functions`, `summary` |

## Agent Instructions

1. `src_dir` should be a path to the source directory (e.g., `"src/codomyrmex"`).
2. `static_analysis_full_audit` combines all audit checks into a single report with summary counts.
3. All tools are read-only and produce no side effects.
4. Results are returned as lists of dicts with `module`, `issue`, and `detail` keys.

## Operating Contracts

- Tools use `pathlib.Path` internally for path handling.
- AST-based import extraction uses Python's `ast` module (no regex).
- Layer violation checking relies on the project's architectural layer hierarchy.

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Primary Tools |
|-----------|-------------|---------------|
| Engineer | Full | All 3 tools |
| Architect | Full | `static_analysis_full_audit` |
| QATester | Read | `static_analysis_audit_exports` |

## Navigation

- [Root](../../../../../../README.md)
