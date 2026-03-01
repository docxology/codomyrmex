# Tool Use Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

Registry, composition, and validation infrastructure for tool-based workflows. Provides a central registry for managing tools, a chain abstraction for sequential tool pipelines, and JSON-schema-like input/output validation utilities.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`ValidationResult`** -- Result of a validation operation (valid flag + error list).
- **`ToolEntry`** -- A registered tool with name, handler, schemas, and tags.
- **`ToolRegistry`** -- Central registry for managing available tools.
- **`ChainStep`** -- A single step in a tool chain pipeline.
- **`ChainResult`** -- Result of executing an entire tool chain.
- **`ToolChain`** -- A pipeline of tools that execute sequentially.

### Functions

- **`validate_input()`** -- Validate tool input data against a JSON-schema-like specification.
- **`validate_output()`** -- Validate tool output data against a JSON-schema-like specification.

### Decorators

- **`@tool()`** -- Decorator that marks a function as a tool and optionally registers it.

## Quick Start

### Register and Invoke a Tool

```python
from codomyrmex.tool_use import ToolRegistry, ToolEntry

registry = ToolRegistry()
registry.register(ToolEntry(
    name="greet",
    description="Say hello",
    handler=lambda data: {"message": f"Hello, {data['name']}!"},
    input_schema={
        "type": "object",
        "required": ["name"],
        "properties": {"name": {"type": "string"}},
    },
))

result = registry.invoke("greet", {"name": "World"})
assert result.ok
print(result.data)  # {"message": "Hello, World!"}
```

### Use the @tool Decorator

```python
from codomyrmex.tool_use import tool, ToolRegistry

registry = ToolRegistry()

@tool(
    name="add",
    description="Add two numbers",
    input_schema={
        "type": "object",
        "required": ["a", "b"],
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
        },
    },
)
def add(data):
    return {"sum": data["a"] + data["b"]}

# Register from the decorator's attached entry
registry.register(add.tool_entry)
result = registry.invoke("add", {"a": 2, "b": 3})
print(result.data)  # {"sum": 5}
```

### Chain Tools Together

```python
from codomyrmex.tool_use import ToolRegistry, ToolEntry, ToolChain, ChainStep

registry = ToolRegistry()

registry.register(ToolEntry(
    name="fetch",
    description="Fetch data",
    handler=lambda data: {"body": f"content for {data.get('url', '')}"},
))
registry.register(ToolEntry(
    name="parse",
    description="Parse content",
    handler=lambda data: {"parsed": data["content"].upper()},
))

chain = ToolChain(registry=registry)
chain.add_step(ChainStep(tool_name="fetch", output_key="raw"))
chain.add_step(ChainStep(
    tool_name="parse",
    input_mapping={"content": "raw.body"},
    output_key="result",
))

result = chain.execute({"url": "https://example.com"})
assert result.success
print(result.context["result"])  # {"parsed": "CONTENT FOR HTTPS://EXAMPLE.COM"}
```

### Validate Input Data

```python
from codomyrmex.tool_use import validate_input

schema = {
    "type": "object",
    "required": ["name", "count"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "count": {"type": "integer", "minimum": 0},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}

result = validate_input({"name": "test", "count": 5, "tags": ["a"]}, schema)
assert result.valid

result = validate_input({"name": "", "count": -1}, schema)
assert not result.valid
print(result.errors)
```

## Directory Structure

- `validation.py` -- JSON-schema-like input/output validation
- `registry.py` -- Tool registry, ToolEntry dataclass, @tool decorator
- `chains.py` -- ToolChain pipeline with ChainStep and ChainResult
- `__init__.py` -- Public API re-exports

## Exports

| Export | Type | Description |
| :--- | :--- | :--- |
| `ValidationResult` | Dataclass | Validation result with valid flag and errors |
| `validate_input` | Function | Validate input data against schema |
| `validate_output` | Function | Validate output data against schema |
| `ToolEntry` | Dataclass | Registered tool definition |
| `ToolRegistry` | Class | Central tool management registry |
| `tool` | Decorator | Mark a function as a tool |
| `ChainStep` | Dataclass | Single step in a tool chain |
| `ChainResult` | Dataclass | Result of chain execution |
| `ToolChain` | Class | Sequential tool pipeline |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/tool_use/ -v
```

## Navigation

- **Extended Docs**: [docs/modules/tool_use/](../../../docs/modules/tool_use/)
- [API_SPECIFICATION](API_SPECIFICATION.md) | [PAI](PAI.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
