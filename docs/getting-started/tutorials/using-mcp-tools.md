# Using MCP Tools

**Audience**: Developers integrating with the Codomyrmex MCP surface

This tutorial walks through discovering and invoking MCP tools exposed by Codomyrmex modules.

## Prerequisites

- Codomyrmex installed (`uv sync`)
- Python 3.10+

## 1. Discover Available Tools

Every module exposes tools via `mcp_tools.py`. List them programmatically:

```python
from codomyrmex.model_context_protocol import get_all_tools

tools = get_all_tools()
print(f"Found {len(tools)} MCP tools across all modules")

# Filter by module
for tool in tools:
    if "security" in tool.module:
        print(f"  {tool.name}: {tool.description[:60]}...")
```

Or from the CLI:

```bash
# Count total tools
uv run python -c "
from codomyrmex.model_context_protocol import get_all_tools
print(f'{len(get_all_tools())} tools registered')
"
```

## 2. Invoke a Tool Directly

Tools are decorated with `@mcp_tool` and can be called as normal Python functions:

```python
from codomyrmex.agentic_memory.rules.mcp_tools import rules_list_modules

result = rules_list_modules()
print(result)  # ['agents', 'agentic_memory', 'cache', ...]
```

## 3. Use Tools via the MCP Bridge

For AI agent integration, tools are exposed through the MCP JSON-RPC protocol:

```python
from codomyrmex.model_context_protocol import MCPBridge

bridge = MCPBridge()

# List tool schemas (for LLM function calling)
schemas = bridge.list_tools()
for schema in schemas[:5]:
    print(f"{schema['name']}: {schema['description'][:50]}...")

# Invoke a tool by name
result = bridge.invoke("rules_list_modules", {})
print(result)
```

## 4. Create Your Own MCP Tool

Add tools to any module's `mcp_tools.py`:

```python
from codomyrmex.model_context_protocol import mcp_tool

@mcp_tool(
    name="my_module_greet",
    description="Greet the user by name",
    module="my_module",
)
def my_module_greet(name: str) -> str:
    \"\"\"Greet the user.

    Args:
        name: The user's name.

    Returns:
        A greeting string.
    \"\"\"
    return f"Hello, {name}! Welcome to Codomyrmex."
```

## Key Metrics

| Metric | Value |
|--------|-------|
| Total `@mcp_tool` decorators (production) | 600 ([inventory](../../reference/inventory.md)) |
| Modules with `mcp_tools.py` | 127 / 127 |
| Tool discovery | Automatic via module scanning |

## Next Steps

- See [SPEC.md](../SPEC.md) for the full MCP protocol specification
- See [creating-a-module](creating-a-module.md) for building new modules with MCP support
- See [connecting-pai.md](connecting-pai.md) for PAI ↔ MCP integration
