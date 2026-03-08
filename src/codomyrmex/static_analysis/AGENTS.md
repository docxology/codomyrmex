# Static Analysis — Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

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

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `static_analysis_audit_exports` | Audit all modules under a source directory for missing `__all__` definitions. | SAFE |
| `static_analysis_find_dead_exports` | Find exports in `__all__` that are never imported anywhere in the codebase. | SAFE |
| `static_analysis_full_audit` | Run the full audit suite (missing `__all__`, dead exports, unused functions) on a source directory. Returns unified report dict. | SAFE |

## Operating Contracts

- **DO:** Call `scan_imports()` before `check_layer_violations()` — violations require the edge list from scan
- **DO:** Pass absolute `Path` objects to all functions
- **DO NOT:** Import analyzed modules during scanning — operates on AST/filesystem only
- **DO NOT:** Modify layer taxonomy without updating `SPEC.md`

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `static_analysis_full_audit`, `static_analysis_audit_exports`, `static_analysis_find_dead_exports` | TRUSTED |
| **Architect** | Analysis only | `static_analysis_full_audit`, `static_analysis_audit_exports` — review without modifying | OBSERVED |
| **QATester** | Validation | `static_analysis_full_audit` — verify quality gates pass after BUILD | OBSERVED |
| **Researcher** | Read-only | `static_analysis_audit_exports`, `static_analysis_find_dead_exports` — codebase surface inspection | SAFE |

### Engineer Agent
**Use Cases**: Running full static analysis pipelines during BUILD phase, detecting missing `__all__` before releases, identifying dead exports as part of cleanup sprints.

### Architect Agent
**Use Cases**: Architectural code review via layer violation scanning, auditing export completeness across modules, reviewing dependency graphs.

### QATester Agent
**Use Cases**: Validating that full audit passes with zero critical findings during VERIFY phase, confirming quality gates after refactoring.

### Researcher Agent
**Use Cases**: Inspecting export surface and dead code patterns to understand codebase structure for research analysis.

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md) — This document
- **Parent**: [../AGENTS.md](../AGENTS.md) — Package coordination

### Sibling Documents

- [README.md](README.md) — Module overview
- [SPEC.md](SPEC.md) — Technical specification


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/static_analysis.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/static_analysis.cursorrules)
