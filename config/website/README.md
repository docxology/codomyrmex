# Website Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Web application server for the Codomyrmex platform. Provides REST API endpoints, CORS configuration, and Ollama LLM integration for the web interface.

## Quick Configuration

```bash
export CODOMYRMEX_CORS_ORIGINS="*"    # Allowed CORS origins (comma-separated)
export CODOMYRMEX_ENV="Development"    # Application environment name
export CODOMYRMEX_OLLAMA_URL="http://localhost:11434"    # Ollama service URL for web LLM features
export CODOMYRMEX_DEFAULT_MODEL="llama3.2:1b"    # Default Ollama model for web interface
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `CODOMYRMEX_CORS_ORIGINS` | str | `*` | Allowed CORS origins (comma-separated) |
| `CODOMYRMEX_ENV` | str | `Development` | Application environment name |
| `CODOMYRMEX_OLLAMA_URL` | str | `http://localhost:11434` | Ollama service URL for web LLM features |
| `CODOMYRMEX_DEFAULT_MODEL` | str | `llama3.2:1b` | Default Ollama model for web interface |

## PAI Integration

PAI agents interact with website through direct Python imports. CORS origins control cross-origin access. Ollama URL must point to a running Ollama instance for LLM features.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep website

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/website/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
