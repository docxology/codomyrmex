# MCP tool specification coverage

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Convention

For each `mcp_tools.py` under `src/codomyrmex/` (excluding `tests/`), the same directory should contain **`MCP_TOOL_SPECIFICATION.md`** documenting exported tools. This matches the RASP pattern used across most top-level modules.

## Audit

Regenerate the gap list:

```bash
uv run python scripts/mcp_spec_gap.py
```

The script prints paths to `mcp_tools.py` files whose directory has no sibling `MCP_TOOL_SPECIFICATION.md`. When the list is empty, every non-test `mcp_tools.py` under `src/codomyrmex/` has a co-located spec.

## Related

- [inventory.md](inventory.md) — `@mcp_tool` and `mcp_tools.py` counts
- [scripts/mcp_spec_gap.py](../../scripts/mcp_spec_gap.py)

## Navigation

- **Parent**: [docs/reference/README.md](README.md)
- **Project root**: [README.md](../../README.md)
