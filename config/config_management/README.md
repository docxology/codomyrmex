# Config Management Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Central configuration management, validation, and deployment for the Codomyrmex ecosystem. Provides multi-source config loading, schema validation, and environment-aware configuration.

## Quick Configuration

```bash
export ENVIRONMENT="development"    # Active environment name (development, staging, production)
export OLLAMA_BASE_URL="http://localhost:11434"    # Base URL for Ollama LLM service
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ENVIRONMENT` | str | `development` | Active environment name (development, staging, production) |
| `OLLAMA_BASE_URL` | str | `http://localhost:11434` | Base URL for Ollama LLM service |

## MCP Tools

This module exposes 3 MCP tool(s):

- `get_config`
- `set_config`
- `validate_config`

## PAI Integration

PAI agents invoke config_management tools through the MCP bridge. Configuration is loaded from YAML files, environment variables, and programmatic defaults. Environment variables take precedence over file values.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep config_management

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/config_management/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
