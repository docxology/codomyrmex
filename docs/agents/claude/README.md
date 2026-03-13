# Claude (Anthropic)

**Module**: `codomyrmex.agents.claude` | **Category**: API-based | **Last Updated**: March 2026

## Overview

Anthropic Claude integration for high-quality code generation, complex reasoning, and agentic coding workflows. Supports Claude 3 Opus/Sonnet/Haiku models with streaming, multi-turn conversations, tool use, and session management.

## Key Classes

| Class | Purpose |
|:---|:---|
| `ClaudeClient` | Full-featured API client with retry logic, tool use, and sessions |
| `ClaudeIntegrationAdapter` | Bridges Claude with other Codomyrmex modules |

## Claude Code Capabilities (v0.2.0)

| Method | Purpose |
|:---|:---|
| `edit_file(path, instruction)` | Apply AI-guided edits to files |
| `create_file(path, description)` | Generate new files from descriptions |
| `review_code(code)` | AI-powered code review |
| `scan_directory(path)` | Project context scanning |
| `generate_diff(before, after)` | Unified diff generation |

## Usage

```python
from codomyrmex.agents.claude import ClaudeClient, ClaudeIntegrationAdapter

# Basic usage
client = ClaudeClient()
response = client.execute(AgentRequest(prompt="Hello, Claude!"))

# With session management
session = client.create_session()
response = client.execute_with_session(request, session=session)

# With tool use
client.register_tool(
    name="get_weather",
    description="Get weather for a location",
    input_schema={"type": "object", "properties": {"location": {"type": "string"}}},
    handler=get_weather_fn,
)
response = client.execute_with_tools(request)

# Claude Code methods
result = client.edit_file("/path/to/file.py", "Add type hints")
review = client.review_code("def add(a, b): return a + b")
structure = client.scan_directory("/path/to/project")
```

## Configuration

**Required API Key**: `ANTHROPIC_API_KEY`

```bash
export ANTHROPIC_API_KEY=your-key-here
```

## Source Module

Source: [`src/codomyrmex/agents/claude/`](../../../../src/codomyrmex/agents/claude/)

| File | Purpose |
|:---|:---|
| `claude_client.py` | API client with retry, streaming, tool use, sessions |
| `claude_integration.py` | Integration adapter for cross-module bridging |
| `mcp_tools.py` | MCP tool definitions for agent consumption |
| `mixins/` | Composable capability mixins |

## Source Documentation

| Document | Path |
|:---|:---|
| README | [claude/README.md](../../../../src/codomyrmex/agents/claude/README.md) |
| SPEC | [claude/SPEC.md](../../../../src/codomyrmex/agents/claude/SPEC.md) |
| API Spec | [claude/API_SPECIFICATION.md](../../../../src/codomyrmex/agents/claude/API_SPECIFICATION.md) |
| MCP Tools | [claude/MCP_TOOL_SPECIFICATION.md](../../../../src/codomyrmex/agents/claude/MCP_TOOL_SPECIFICATION.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/claude/](../../../../src/codomyrmex/agents/claude/)
- **Project Root**: [README.md](../../../README.md)
