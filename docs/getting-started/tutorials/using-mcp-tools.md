# Using MCP Tools

**Audience**: Developers integrating with the Codomyrmex MCP surface

This tutorial walks through discovering and invoking MCP tools exposed by Codomyrmex modules.

## Prerequisites

- Codomyrmex installed (`uv sync`)
- Python 3.11+

## 1. Discover Available Tools

Every module exposes tools via `mcp_tools.py`. The PAI MCP bridge discovers them (plus its static proxy tools) into one registry; list them programmatically:

```python
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry

registry = get_tool_registry()
tools = registry.list_tools()  # sorted names, e.g. "codomyrmex.rules_list_modules"
print(f"Found {len(tools)} MCP tools across all modules")

# Filter by name
for name in tools:
    if "security" in name:
        schema = registry.get(name)["schema"]
        print(f"  {name}: {schema['description'][:60]}...")
```

Or from the CLI:

```bash
# Count total tools
uv run python -c "
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry
print(f'{len(get_tool_registry().list_tools())} tools registered')
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

For AI agent integration, tools are exposed through the MCP JSON-RPC protocol (`create_codomyrmex_mcp_server()`); from Python, use the same registry and the trust-gated `call_tool`:

```python
from codomyrmex.agents.pai.mcp_bridge import call_tool, get_tool_registry
from codomyrmex.agents.pai.trust_gateway import trust_tool

registry = get_tool_registry()

# List tool schemas (for LLM function calling)
for name in registry.list_tools()[:5]:
    schema = registry.get(name)["schema"]  # {"name", "description", "inputSchema"}
    print(f"{schema['name']}: {schema['description'][:50]}...")

# Invoke a tool by name; tools are untrusted until approved
trust_tool("codomyrmex.rules_list_modules")
result = call_tool("codomyrmex.rules_list_modules")
print(result["result"])  # failures come back as {"error": {...}}
```

## 4. Create Your Own MCP Tool

Add tools to any module's `mcp_tools.py`:

```python
from codomyrmex.model_context_protocol import mcp_tool

@mcp_tool(
    name="my_module_greet",
    description="Greet the user by name",
    category="my_module",
)
def my_module_greet(name: str) -> str:
    """Greet the user.

    Args:
        name: The user's name.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}! Welcome to Codomyrmex."
```

## Key Metrics

| Metric | Value |
| --- | --- |
| Total `@mcp_tool` decorators (production) | 600 ([inventory](../../reference/inventory.md)) |
| Modules with `mcp_tools.py` | 127 / 127 |
| Tool discovery | Automatic via module scanning |

## Next Steps

- See [SPEC.md](../SPEC.md) for the full MCP protocol specification
- See [creating-a-module](creating-a-module.md) for building new modules with MCP support
- See [connecting-pai.md](connecting-pai.md) for PAI ↔ MCP integration
