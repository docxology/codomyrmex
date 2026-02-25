# Static Analysis Module — MCP Tool Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## Overview

The `static_analysis` module does **not** expose any MCP tools. Its functions are accessible exclusively via direct Python import.

## Reason

Static analysis operates on local filesystem paths and produces structured data objects (lists of dicts, dataclasses). These functions are designed for direct programmatic use within build pipelines, CI/CD workflows, and the Codomyrmex CLI — not for agent tool dispatch.

## Python API

All functionality is available via Python import:

```python
from codomyrmex.static_analysis.imports import scan_imports, check_layer_violations, extract_imports_ast
from codomyrmex.static_analysis.exports import audit_exports, find_dead_exports, find_unused_functions, full_audit
```

See `API_SPECIFICATION.md` for full function signatures and usage examples.

## CLI Access

Static analysis is available through the Codomyrmex CLI:

```bash
codomyrmex analyze <path>
```
