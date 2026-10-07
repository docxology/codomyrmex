<!-- agents: curated -->

# Preprocessing Module — Agent Coordination

## Purpose

Reader-facing mirror for `codomyrmex.preprocessing`, a deliberately small module
whose only public surface is one deterministic MCP tool for normalizing text.
Normative behavior lives in
[`src/codomyrmex/preprocessing/`](../../../src/codomyrmex/preprocessing/AGENTS.md).

## Key Capabilities

- `preprocess_data(data: str) -> dict` (in `mcp_tools.py`, registered with
  `@mcp_tool(category="preprocessing")`): returns
  `{"status": "success", "preprocessed": data.strip().lower()}`.
- The package `__init__.py` exports nothing; import the tool from
  `codomyrmex.preprocessing.mcp_tools`.

## Agent Usage Patterns

```python
from codomyrmex.preprocessing.mcp_tools import preprocess_data

result = preprocess_data("  Hello World  ")
assert result == {"status": "success", "preprocessed": "hello world"}
```

## Integration Points

- **Source**: [src/codomyrmex/preprocessing/](../../../src/codomyrmex/preprocessing/)
- **MCP contract**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/preprocessing/MCP_TOOL_SPECIFICATION.md)
- **Tests**: [tests/unit/preprocessing/test_mcp_tools.py](../../../tests/unit/preprocessing/test_mcp_tools.py)
- **Docs**: [Module Documentation](README.md) · [PAI notes](PAI.md)
- **Spec**: [Technical Specification](SPEC.md)
- **Module index**: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Treat the source module and its tests as authoritative; update this mirror
  when the tool's signature or return shape changes.
- The tool has no error branch: non-`str` input raises `AttributeError`, so
  callers validate type and size before invoking it.
- Keep preprocessing deterministic and side-effect free (no network, no
  filesystem access).
- This file is hand-reviewed (`agents: curated`), so the module enricher
  (`scripts/documentation/enrich_module_docs.py`) leaves it alone; edit it by
  hand and re-run `make docs-check`.
