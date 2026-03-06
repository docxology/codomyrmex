# Website Configuration Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Web application server for the Codomyrmex platform. Provides REST API endpoints, CORS configuration, and Ollama LLM integration for the web interface. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `CODOMYRMEX_CORS_ORIGINS` | string | No | `*` | Allowed CORS origins (comma-separated) |
| `CODOMYRMEX_ENV` | string | No | `Development` | Application environment name |
| `CODOMYRMEX_OLLAMA_URL` | string | No | `http://localhost:11434` | Ollama service URL for web LLM features |
| `CODOMYRMEX_DEFAULT_MODEL` | string | No | `llama3.2:1b` | Default Ollama model for web interface |

## Environment Variables

```bash
# Optional (defaults shown)
export CODOMYRMEX_CORS_ORIGINS="*"    # Allowed CORS origins (comma-separated)
export CODOMYRMEX_ENV="Development"    # Application environment name
export CODOMYRMEX_OLLAMA_URL="http://localhost:11434"    # Ollama service URL for web LLM features
export CODOMYRMEX_DEFAULT_MODEL="llama3.2:1b"    # Default Ollama model for web interface
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

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/website/SPEC.md)
