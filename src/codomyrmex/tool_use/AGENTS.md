# Tool Use Module — Agent Coordination

## Purpose

Tool Use Module

Registry, composition, and validation for tool-based workflows.
Provides a central registry for managing tools, a chain abstraction
for sequential tool pipelines, and input/output validation utilities.

## Key Capabilities

- **`ValidationResult`** -- Result of a validation operation (valid flag + error list).
- **`ToolEntry`** -- A registered tool with name, handler, schemas, and tags.
- **`ToolRegistry`** -- Central registry for managing available tools.
- **`ChainStep`** -- A single step in a tool chain pipeline.
- **`ChainResult`** -- Result of executing an entire tool chain.
- **`ToolChain`** -- A pipeline of tools that execute sequentially.
- **`validate_input()`** -- Validate tool input data against a JSON-schema-like specification.
- **`validate_output()`** -- Validate tool output data against a JSON-schema-like specification.

## Agent Usage Patterns

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

## Key Components

| Export | Type |
|--------|------|
| `ValidationResult` | Public API |
| `validate_input` | Public API |
| `validate_output` | Public API |
| `ToolEntry` | Public API |
| `ToolRegistry` | Public API |
| `tool` | Public API |
| `ChainStep` | Public API |
| `ChainResult` | Public API |
| `ToolChain` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `chains.py` | Tool chain composition for sequential tool execution. |
| `registry.py` | Tool registry for managing available tools. |
| `validation.py` | Input/output validation for tool calls. |

## Integration Points

- **Docs**: [Module Documentation](../../../docs/modules/tool_use/README.md)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tool_use -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
