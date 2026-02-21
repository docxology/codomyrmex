# Tool Use Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Registry, composition, and validation infrastructure for tool-based workflows. Provides a central registry for managing tools, a chain abstraction for sequential tool pipelines, and JSON-schema-like input/output validation utilities.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`ToolRegistry`** -- Central registry for managing available tools.
- **`@tool()`** -- Decorator that marks a function as a tool and optionally registers it.
- **`ToolChain`** -- Pipeline of tools that execute sequentially with input/output mapping.
- **`validate_input()` / `validate_output()`** -- JSON-schema-like validation for tool data.

## Quick Start

```python
from codomyrmex.tool_use import ToolRegistry, ToolEntry, tool

registry = ToolRegistry()

@tool(name="add", description="Add two numbers",
      input_schema={"type": "object", "required": ["a", "b"],
                    "properties": {"a": {"type": "number"}, "b": {"type": "number"}}})
def add(data):
    return {"sum": data["a"] + data["b"]}

registry.register(add.tool_entry)
result = registry.invoke("add", {"a": 2, "b": 3})
print(result.data)  # {"sum": 5}
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `ToolEntry` | Registered tool with name, handler, schemas, and tags |
| `ToolRegistry` | Central tool management registry |
| `ChainStep` | Single step in a tool chain pipeline |
| `ChainResult` | Result of executing an entire tool chain |
| `ToolChain` | Sequential tool pipeline |
| `ValidationResult` | Result of a validation operation |

### Functions and Decorators

| Export | Description |
|--------|-------------|
| `@tool()` | Decorator to mark a function as a tool |
| `validate_input()` | Validate input data against a schema |
| `validate_output()` | Validate output data against a schema |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tool_use -v
```

## Related Modules

- [Model Context Protocol](../model_context_protocol/README.md)
- [Schemas](../schemas/README.md)

## Navigation

- **Source**: [src/codomyrmex/tool_use/](../../../src/codomyrmex/tool_use/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/tool_use/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/tool_use/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
