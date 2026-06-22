# system_discovery

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module implementation, resources, and local coordination for System Discovery..

## Module Catalog

Use `build_module_catalog()` for a read-only view of top-level
`src/codomyrmex` entries, runtime-module counts, support surfaces,
`docs/modules` coverage, and docs/API/MCP/test parity. This helper is additive
and does not change `codomyrmex.list_modules()`.

## Structure Audit

Use `structure_audit.audit_module_structure()` or
`uv run python scripts/src_structure_audit.py --json` to turn catalog parity
into a gate-friendly pass/fail report. The audit is read-only and covers
runtime module docs/API/MCP/test parity, PEP 561 `py.typed` markers,
support-surface docs, missing docs/modules counterparts, orphaned docs/modules
directories, and retired module names.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `PAI.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `core/` – Subdirectory
- `health/` – Subdirectory
- `mcp_tools.py` – File
- `module_catalog.py` – File
- `py.typed` – File
- `reporting/` – Subdirectory
- `structure_audit.py` – File

## Navigation
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
