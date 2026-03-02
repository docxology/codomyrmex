# Personal AI Infrastructure — Static Analysis Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Static Analysis module provides import scanning, layer violation detection, and export auditing for Python codebases. It powers the PAI Algorithm's VERIFY phase by detecting architectural drift, circular dependencies, and missing `__all__` declarations.

## PAI Capabilities

### Import Scanning

```python
from codomyrmex.static_analysis import scan_imports, check_layer_violations

# Scan all imports in the source tree
edges = scan_imports("src/codomyrmex")
# Returns: list of (source_module, imported_module) edges

# Check for architectural layer violations
violations = check_layer_violations(edges)
for v in violations:
    print(f"{v['src']} → {v['dst']}: {v['reason']}")
```

### Export Auditing

```python
from codomyrmex.static_analysis import audit_exports, check_all_defined

# Audit all module exports for completeness
findings = audit_exports("src/codomyrmex")
for f in findings:
    print(f"{f['module']}: {f['detail']}")

# Check that __all__ is defined and accurate
issues = check_all_defined("src/codomyrmex/security")
```

### AST-Based Analysis

```python
from codomyrmex.static_analysis import extract_imports_ast

# Extract imports via AST parsing (more accurate than regex)
imports = extract_imports_ast("src/codomyrmex/agents/__init__.py")
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `scan_imports` | Function | Scan all imports across a source tree |
| `check_layer_violations` | Function | Detect architectural layer boundary violations |
| `extract_imports_ast` | Function | AST-based import extraction from a single file |
| `audit_exports` | Function | Audit `__all__` declarations for completeness |
| `check_all_defined` | Function | Verify `__all__` accuracy for a module |

## PAI Algorithm Phase Mapping

| Phase | Static Analysis Contribution |
|-------|------------------------------|
| **OBSERVE** | `scan_imports` maps the dependency graph for codebase understanding |
| **THINK** | Import edge data informs reasoning about module relationships |
| **VERIFY** | `check_layer_violations` catches architectural drift; `audit_exports` ensures API completeness |
| **LEARN** | Analysis results feed into maintenance and refactoring recommendations |

## Architecture Role

**Core Layer** — Foundational code intelligence consumed by `security/`, `maintenance/`, `coding/`, and the MCP `analyze_python_file` tool.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.static_analysis import ...`
- CLI: `codomyrmex static_analysis <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
