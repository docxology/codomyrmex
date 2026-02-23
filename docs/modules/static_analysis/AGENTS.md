# Static Analysis — Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Provides AST-based static analysis for import dependency scanning and export auditing. This module enables automated detection of layer-boundary violations and missing `__all__` exports across the Codomyrmex package.

## Active Components

- `__init__.py` — Public API: `scan_imports`, `check_layer_violations`, `extract_imports_ast`, `audit_exports`, `check_all_defined`
- `imports.py` — Import graph scanning, layer classification, and violation detection
- `exports.py` — Module export auditing and `__all__` verification

## Public API

### `scan_imports(src_dir: Path) → List[Dict[str, Any]]`

Walks all `.py` files under `src_dir`, extracting cross-module `codomyrmex.*` imports via AST. Returns edges with `src`, `dst`, `file`, `src_layer`, `dst_layer` fields.

### `check_layer_violations(edges: List[Dict]) → List[Dict]`

Applies layer-boundary rules to import edges. Returns violations where lower layers import higher layers.

### `extract_imports_ast(filepath: Path) → List[str]`

Extracts codomyrmex module names imported by a single file using AST parsing.

### `audit_exports(src_dir: Path) → List[Dict[str, str]]`

Scans all module `__init__.py` files for `__all__` definitions. Returns findings for modules missing `__all__`.

### `check_all_defined(init_path: Path) → Tuple[bool, Union[List[str], None]]`

Parses a single `__init__.py` and returns whether `__all__` is defined and its contents.

## Layer Classification

Modules are classified into architectural layers for violation detection:

| Layer | SPEC.md Name | Modules |
| :--- | :--- | :--- |
| Foundation | Foundation | `logging_monitoring`, `environment_setup`, `model_context_protocol`, `terminal_interface`, `config_management`, `telemetry` |
| Core | Core | `coding`, `static_analysis`, `data_visualization`, `search`, `git_operations`, `security`, `llm`, `performance`, `cache`, `compression`, `encryption`, `networking`, `serialization`, `scrape`, `documents` |
| Service | Service | `documentation`, `api`, `ci_cd_automation`, `containerization`, `database_management`, `logistics`, `orchestrator`, `auth`, `cloud`, `deployment` |
| Specialized | Specialized | All remaining modules |

## Operating Contracts

- Operates on the filesystem; does not import analyzed modules (safe for circular dependency detection)
- Uses only `ast`, `os`, `pathlib` from stdlib — no external dependencies
- Layer taxonomy must stay aligned with [SPEC.md](../SPEC.md)

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md) — This document
- **Parent**: [../AGENTS.md](../AGENTS.md) — Package coordination

### Sibling Documents

- [README.md](README.md) — Module overview
- [SPEC.md](SPEC.md) — Technical specification
