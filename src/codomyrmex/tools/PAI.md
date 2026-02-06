# Personal AI Infrastructure — Tools Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Tools module provides PAI integration for managing external development tools.

## PAI Capabilities

### Tool Execution

Run external tools:

```python
from codomyrmex.tools import ToolRunner

runner = ToolRunner()
result = runner.run("ruff", ["check", "src/"])

print(f"Exit code: {result.returncode}")
print(result.stdout)
```

### Tool Discovery

Find available tools:

```python
from codomyrmex.tools import ToolRegistry

registry = ToolRegistry()
tools = registry.discover()

for tool in tools:
    print(f"{tool.name}: {tool.version}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `ToolRunner` | Execute tools |
| `ToolRegistry` | Discover tools |
| `OutputParser` | Parse tool output |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
