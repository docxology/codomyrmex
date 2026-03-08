# Agents -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the agents module. AI agent framework integrations supporting 13 agentic frameworks including Claude, Codex, Gemini, Jules, and more.

## Configuration Requirements

Before using agents in any PAI workflow, ensure:

1. `AGENT_DEFAULT_TIMEOUT` is set (default: `30`) -- Default timeout in seconds for agent operations
2. `AGENT_ENABLE_LOGGING` is set (default: `true`) -- Enable or disable agent execution logging
3. `ANTHROPIC_API_KEY` is set -- API key for Claude agent integration
4. `OPENAI_API_KEY` is set -- API key for Codex/O1 agent integration
5. `GEMINI_API_KEY` is set -- API key for Gemini agent integration

## Agent Instructions

1. Verify required environment variables are set before invoking agents tools
2. Use `get_config("agents.<key>")` from config_management to read module settings
3. Available MCP tools: `execute_agent`, `list_agents`, `get_agent_memory`
4. Each agent provider requires its own API key. CLI-based agents (Jules, OpenCode) require the respective CLI tool installed on PATH.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("agents.setting")

# Update configuration
set_config("agents.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/agents/AGENTS.md)
