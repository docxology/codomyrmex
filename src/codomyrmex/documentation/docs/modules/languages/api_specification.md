# Languages - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `languages` module provides utilities for interacting with various programming languages, including checking installation status, providing installation instructions, setting up projects, and running scripts.

## 2. Core Components

### 2.1 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_mcp_tools` | `() -> None` | Register all language-related MCP tools for agent consumption |

### 2.2 MCP Tools (via `mcp_tools.py`)

Language management tools are primarily exposed via MCP for agent-driven interactions: checking if languages are installed, getting install instructions, and executing scripts.

## 3. Usage Example

```python
from codomyrmex.languages import register_mcp_tools

register_mcp_tools()
# MCP tools are now available for agents to discover and use
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
