# static_analysis

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

AST-only package audits for imports, architectural layers, explicit
file-scoped integration contracts, and public exports. Run the repository
gates with:

```bash
uv run --locked python scripts/audits/audit_imports.py --root .
uv run --locked python scripts/audits/audit_exports.py --root .
```

The import gate rejects unexplained upward dependencies and stale exception
contracts. The export gate requires a non-empty `__all__` for every runtime
module.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `exports.py` – File
- `imports.py` – File
- `mcp_tools.py` – File
- `py.typed` – File

## Navigation
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
