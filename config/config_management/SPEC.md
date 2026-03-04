# Config Management Configuration Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Central configuration management, validation, and deployment for the Codomyrmex ecosystem. Provides multi-source config loading, schema validation, and environment-aware configuration. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `ENVIRONMENT` | string | No | `development` | Active environment name (development, staging, production) |
| `OLLAMA_BASE_URL` | string | No | `http://localhost:11434` | Base URL for Ollama LLM service |

## Environment Variables

```bash
# Optional (defaults shown)
export ENVIRONMENT="development"    # Active environment name (development, staging, production)
export OLLAMA_BASE_URL="http://localhost:11434"    # Base URL for Ollama LLM service
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- All configuration options have sensible defaults
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/config_management/SPEC.md)
