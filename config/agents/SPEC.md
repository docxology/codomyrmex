# Agents Configuration Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

AI agent framework integrations supporting 13 agentic frameworks including Claude, Codex, Gemini, Jules, and more. Provides API-based and CLI-based agent clients with orchestration. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `AGENT_DEFAULT_TIMEOUT` | string | No | `30` | Default timeout in seconds for agent operations |
| `AGENT_ENABLE_LOGGING` | string | No | `true` | Enable or disable agent execution logging |
| `ANTHROPIC_API_KEY` | string | Yes | None | API key for Claude agent integration |
| `OPENAI_API_KEY` | string | Yes | None | API key for Codex/O1 agent integration |
| `GEMINI_API_KEY` | string | Yes | None | API key for Gemini agent integration |

## Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY=""    # API key for Claude agent integration
export OPENAI_API_KEY=""    # API key for Codex/O1 agent integration
export GEMINI_API_KEY=""    # API key for Gemini agent integration

# Optional (defaults shown)
export AGENT_DEFAULT_TIMEOUT="30"    # Default timeout in seconds for agent operations
export AGENT_ENABLE_LOGGING="true"    # Enable or disable agent execution logging
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `ANTHROPIC_API_KEY` must be set before module initialization
- `OPENAI_API_KEY` must be set before module initialization
- `GEMINI_API_KEY` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/agents/SPEC.md)
