# Data Curation Documentation Mirror Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Purpose

This file records the documentation-site contract for the data curation mirror.
The source specification at `src/codomyrmex/data_curation/SPEC.md` remains the
authoritative technical reference for MinHash signatures, LSH banding, and the
`DataCurator` deduplication pipeline.

## Mirror Contract

- Describe only the implemented pure-Python + NumPy MinHash and LSH behavior.
- Keep the quick-start example aligned with `DataCurator.deduplicate`.
- Preserve the documented first-occurrence-wins duplicate removal behavior.
- Keep MCP tool names and payloads synchronized with `mcp_tools.py`.
- Use lower-case local links for this generated docs tree.

## Validation

After changing this mirror or the source module, run:

```bash
make docs-check
uv run ruff check src/codomyrmex/data_curation
uv run pytest src/codomyrmex/tests/unit/data_curation/ -q
```

## Navigation

- **Module Overview**: README.md is rendered in this mirror as [readme.md](readme.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [api_specification.md](api_specification.md)
- **MCP Tools**: [mcp_tool_specification.md](mcp_tool_specification.md)
- **Source Specification**: [../../../../data_curation/SPEC.md](../../../../data_curation/SPEC.md)
