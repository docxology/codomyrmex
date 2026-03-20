# Repository inventory (metrics)

Single source of truth for counts used in documentation and marketing copy. **Refresh** after large changes to modules, tools, or tests.

**Last updated:** 2026-03-19

## Definitions

| Term | Meaning |
|------|---------|
| **Top-level modules** | Directories under `src/codomyrmex/` that contain `__init__.py`, excluding `tests/`. Each is one Codomyrmex package surface. |
| **`@mcp_tool` count** | Physical lines starting with `@mcp_tool` in `.py` files under `src/codomyrmex/`, excluding paths containing `tests/`. **595** on a full tree walk. |
| **`mcp_tools.py` files** | Files named `mcp_tools.py` under `src/codomyrmex/`, excluding `*/tests/*`. |
| **Collected tests** | Items reported by `uv run pytest --collect-only -q` when collection completes without errors. |

Hermes exposes a **separate** MCP surface (CLI + integration tools). See [docs/agents/hermes/codomyrmex_integration.md](../agents/hermes/codomyrmex_integration.md) for Hermes-specific counts.

## Current values

| Metric | Value (as of last update) |
|--------|---------------------------|
| Top-level modules | 128 |
| `mcp_tools.py` files (non-test) | 149 |
| Production `@mcp_tool` decorators | 595 (see definitions) |
| Pytest tests collected | 34,492 (`uv run pytest --collect-only -q --no-cov`) |

## Reproduce

From the repository root:

```bash
# All metrics in one place
uv run python scripts/doc_inventory.py

# Or manually:
# rg '^@mcp_tool' src/codomyrmex --glob '*.py' --no-ignore | grep -v '/tests/' | wc -l
find src/codomyrmex -name 'mcp_tools.py' -not -path '*/tests/*' | wc -l
uv run pytest --collect-only -q --no-cov 2>&1 | tail -3
```

Top-level module count (Python):

```python
import os
root = "src/codomyrmex"
skip = {"tests", "__pycache__"}
mods = [
    d for d in os.listdir(root)
    if os.path.isdir(os.path.join(root, d))
    and d not in skip
    and os.path.isfile(os.path.join(root, d, "__init__.py"))
]
print(len(mods))
```

## Signposting

- [Reference index](README.md)
- [Documentation guidelines](../development/documentation.md) — Mermaid and maintenance scripts
