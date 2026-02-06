# Personal AI Infrastructure — Examples Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Examples module provides PAI integration demonstrations.

## PAI Capabilities

### Running Examples

Execute example code:

```bash
# List all examples
python -m codomyrmex.examples --list

# Run a specific example
python -m codomyrmex.examples.basic_llm
```

### Creating Examples

Add new examples:

```python
# examples/my_example.py
\"\"\"Example: Using the LLM module.\"\"\"


from codomyrmex.llm import LLMClient

client = LLMClient()
response = client.complete("Hello!")
print(response)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `examples` | Runnable demos |
| `--list` | List examples |
| `docs` | Example docs |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
