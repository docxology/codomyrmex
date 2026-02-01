# examples

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This directory contains executable examples and demonstrations showcasing Codomyrmex capabilities. Examples are designed to be self-contained, runnable, and educational.

## Directory Contents

- `basic_usage/` – Introductory examples for getting started
- `advanced/` – Complex workflows and integrations
- `ai_workflows/` – AI-assisted development patterns
- `module_integration/` – Cross-module usage examples

## Getting Started

```bash
# Run a basic example
cd examples/basic_usage
python hello_codomyrmex.py

# Run with uv
uv run python examples/basic_usage/hello_codomyrmex.py
```

## Example Categories

| Category | Description |
|----------|-------------|
| **Basic Usage** | Simple examples demonstrating core functionality |
| **AI Workflows** | LLM integration, agent coordination, code generation |
| **Module Integration** | Examples combining multiple modules |
| **Advanced** | Complex pipelines, production patterns |

## Writing Examples

When adding new examples:

1. **Self-contained**: Include all necessary imports and setup
2. **Documented**: Add docstrings explaining what the example demonstrates
3. **Runnable**: Ensure the example can be executed directly
4. **Error handling**: Include graceful fallbacks for missing dependencies

## Navigation

- **Project Root**: [../README.md](../README.md)
- **Scripts Examples**: [../scripts/](../scripts/)
- **Documentation**: [../docs/examples/](../docs/examples/)
