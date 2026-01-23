# Personal AI Infrastructure - Configuration Context

**Directory**: `config/`
**Status**: Active

## Overview

The `config/` directory contains template and example configuration files for various modules in the Codomyrmex ecosystem. It is **not** a Python module and does not contain executable code.

## AI Context

When working with configuration:

1. **Templates are Read-Only References**: Files here are templates. Copy them to your working directory or project before modifying.
2. **Environment Variables**: Most configurations support environment variable overrides. Prefer env vars for secrets.
3. **Validation**: Always validate configuration files using the `config_management` module before deploying.

## Key Subdirectories

- `llm/`: LLM provider configurations (Ollama, OpenAI, etc.)
- `security/`: Security and API key templates
- `workflows/`: Workflow configuration examples

## Navigation

- **Parent**: [../README.md](../README.md)
- **Related**: [src/codomyrmex/config_management/](../src/codomyrmex/config_management/)
