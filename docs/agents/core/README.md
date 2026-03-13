# Core Agent Infrastructure

**Module**: `codomyrmex.agents.core` | **Category**: Infrastructure | **Last Updated**: March 2026

## Overview

Base classes, protocols, configuration, and shared infrastructure for all 38 AI agent integrations. Every agent module inherits from the types defined here.

## Key Classes

### Base Types

| Class | Purpose |
|:---|:---|
| `AgentInterface` | Abstract interface all agents implement |
| `BaseAgent` | Common base with execute/session logic |
| `AgentProtocol` | Protocol for structural typing |
| `AgentRequest` | Typed request dataclass (prompt, context, tools) |
| `AgentResponse` | Typed response dataclass (content, tool_calls, metadata) |
| `AgentCapabilities` | Capability declarations (streaming, tools, vision) |
| `AgentIntegrationAdapter` | Cross-module integration bridge |

### Configuration

| Class | Purpose |
|:---|:---|
| `AgentConfig` | Typed agent configuration |
| `get_config()` | Load agent config from YAML |
| `set_config()` / `reset_config()` | Runtime config management |

### Messages & Parsing

| Class | Purpose |
|:---|:---|
| `AgentMessage` | Typed message with role/content |
| `MessageRole` | Enum: system, user, assistant, tool |
| `ToolCall` / `ToolResult` | Tool invocation and response types |
| `parse_code_blocks()` | Extract code blocks from responses |
| `parse_json_response()` | Extract structured JSON from responses |
| `clean_response()` | Strip markdown artifacts |

### Exceptions

| Exception | Purpose |
|:---|:---|
| `AgentError` | Base exception for all agents |
| `AgentConfigurationError` | Config loading/validation errors |
| `AgentTimeoutError` | Execution timeout |
| `ClaudeError`, `GeminiError`, etc. | Per-agent typed exceptions |

### Advanced

| Class | Purpose |
|:---|:---|
| `ReActAgent` | Reason-Act loop agent implementation |

## Usage

```python
from codomyrmex.agents.core import (
    AgentRequest, AgentResponse, BaseAgent,
    parse_code_blocks, get_config,
)

# Create a request
request = AgentRequest(prompt="Analyze this code", context={"file": "main.py"})

# Parse response
blocks = parse_code_blocks(response.content)
```

## Source Module

Source: [`src/codomyrmex/agents/core/`](../../../../src/codomyrmex/agents/core/)

| File | Purpose |
|:---|:---|
| `base.py` | AgentInterface, BaseAgent, request/response dataclasses |
| `config.py` | AgentConfig, YAML loading, runtime management |
| `exceptions.py` | Full exception hierarchy for all agents |
| `messages.py` | Message types, roles, tool calls |
| `parsers.py` | Code block, JSON, structured output parsing |
| `react.py` | ReAct agent implementation |
| `registry.py` | Agent registry for service discovery |
| `session.py` | Session management and persistence |
| `thinking_agent.py` | Chain-of-thought agent wrapper |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/core/](../../../../src/codomyrmex/agents/core/)
- **Project Root**: [README.md](../../../README.md)
