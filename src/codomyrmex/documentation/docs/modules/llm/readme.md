# Llm

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

LLM integration modules for Codomyrmex.

## Architecture Overview

```
llm/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`safety`**
- **`multimodal`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `generate_text` | Safe |
| `list_local_models` | Safe |
| `query_fabric_metadata` | Safe |
| `reason` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/llm/](../../../../src/codomyrmex/llm/)
- **Parent**: [All Modules](../README.md)
