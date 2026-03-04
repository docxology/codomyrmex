# Agents Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

AI agent framework integrations supporting 13 agentic frameworks including Claude, Codex, Gemini, Jules, and more. Provides API-based and CLI-based agent clients with orchestration.

## Quick Configuration

```bash
export AGENT_DEFAULT_TIMEOUT="30"    # Default timeout in seconds for agent operations
export AGENT_ENABLE_LOGGING="true"    # Enable or disable agent execution logging
export ANTHROPIC_API_KEY=""    # API key for Claude agent integration (required)
export OPENAI_API_KEY=""    # API key for Codex/O1 agent integration (required)
export GEMINI_API_KEY=""    # API key for Gemini agent integration (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `AGENT_DEFAULT_TIMEOUT` | str | `30` | Default timeout in seconds for agent operations |
| `AGENT_ENABLE_LOGGING` | str | `true` | Enable or disable agent execution logging |
| `ANTHROPIC_API_KEY` | str | None | API key for Claude agent integration |
| `OPENAI_API_KEY` | str | None | API key for Codex/O1 agent integration |
| `GEMINI_API_KEY` | str | None | API key for Gemini agent integration |

## MCP Tools

This module exposes 3 MCP tool(s):

- `execute_agent`
- `list_agents`
- `get_agent_memory`

## PAI Integration

PAI agents invoke agents tools through the MCP bridge. Each agent provider requires its own API key. CLI-based agents (Jules, OpenCode) require the respective CLI tool installed on PATH.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep agents

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/agents/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
