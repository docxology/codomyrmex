# Agent Guidelines - Tools

## Module Overview

External tool integration and management.

## Key Classes

- **ToolRegistry** — Registry of available tools
- **ToolRunner** — Execute tools
- **ToolConfig** — Tool configuration
- **ToolResult** — Execution result

## Agent Instructions

1. **Discover tools** — Check availability first
2. **Version check** — Verify tool versions
3. **Timeout** — Set execution timeouts
4. **Parse output** — Structure tool output
5. **Log execution** — Track tool usage

## Common Patterns

```python
from codomyrmex.tools import ToolRegistry, ToolRunner

# Check available tools
registry = ToolRegistry()
available = registry.discover()
print(f"Found: {[t.name for t in available]}")

# Check specific tool
if registry.is_available("git"):
    version = registry.get_version("git")
    print(f"git version: {version}")

# Run tools
runner = ToolRunner()
result = runner.run("ruff", ["check", "src/"])

if result.success:
    print(result.stdout)
else:
    print(f"Error: {result.stderr}")

# With timeout
result = runner.run("slow_tool", [], timeout=60)
```

## Testing Patterns

```python
# Verify tool discovery
registry = ToolRegistry()
tools = registry.discover()
assert len(tools) > 0

# Verify tool execution
runner = ToolRunner()
result = runner.run("echo", ["test"])
assert result.success
assert "test" in result.stdout
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
