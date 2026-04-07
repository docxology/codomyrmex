# Repository inventory (metrics)

Single source of truth for counts used in documentation and marketing copy. **Refresh** after large changes to modules, tools, or tests.

**Last updated:** 2026-04-07

## Definitions

| Term | Meaning |
|------|---------|
| **Top-level modules** | Directories under `src/codomyrmex/` that contain `__init__.py`, excluding `tests/`. Each is one Codomyrmex package surface. |
| **Agent packages** | Direct child directories of `src/codomyrmex/agents/` with `__init__.py` (excluding `__pycache__`). Documented under `docs/agents/`; **`docs/agents/rules/`** is docs-only. **39** packages. |
| **`@mcp_tool` count** | Physical lines starting with `@mcp_tool` in `.py` files under `src/codomyrmex/`, excluding paths containing `tests/`. Matches `uv run python scripts/doc_inventory.py`. |
| **`mcp_tools.py` files** | Files named `mcp_tools.py` under `src/codomyrmex/`, excluding `*/tests/*`. |
| **Collected tests** | Items reported by `uv run pytest --collect-only -q --no-cov` when collection completes without errors. |

Hermes exposes a **separate** MCP surface (CLI + integration tools). See [docs/agents/hermes/codomyrmex_integration.md](../agents/hermes/codomyrmex_integration.md) for Hermes-specific counts.

## Current values

| Metric | Value (as of last update) |
|--------|---------------------------|
| Top-level modules | 128 |
| Agent packages (`src/codomyrmex/agents/`) | 39 |
| `mcp_tools.py` files (non-test) | 149 |
| Production `@mcp_tool` decorators | 600 |
| Pytest tests collected | 35,918 (`uv run pytest --collect-only -q --no-cov`; or `uv run python scripts/doc_inventory.py --pytest`) |
| GitHub Actions workflow files (`.github/workflows/*.yml`) | 37 |
| Markdown files under `docs/` | 1,168 (`find docs -name '*.md' -type f \| wc -l`) |

## Reproduce

From the repository root:

```bash
# All metrics in one place (includes `.github/workflows` *.yml count)
uv run python scripts/doc_inventory.py

# Or manually:
# rg '^@mcp_tool' src/codomyrmex --glob '*.py' --no-ignore | grep -v '/tests/' | wc -l
find src/codomyrmex -name 'mcp_tools.py' -not -path '*/tests/*' | wc -l
uv run pytest --collect-only -q --no-cov 2>&1 | tail -3
find docs -name '*.md' -type f | wc -l
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
- [RASP gap report](../plans/agents-readme-gap-report.md) — `uv run python scripts/rasp_gap_report.py`
- [MCP tool spec coverage](mcp-tool-spec-coverage.md) — sibling `MCP_TOOL_SPECIFICATION.md` audit (`scripts/mcp_spec_gap.py`)
- [Documentation guidelines](../development/documentation.md) — Mermaid and maintenance scripts
