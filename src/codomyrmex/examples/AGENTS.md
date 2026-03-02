# Agent Guidelines - Examples

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Reference implementations, demonstrations, and validation reports.

## Contents

- **Usage patterns** — Common Codomyrmex usage patterns
- **Integration examples** — Multi-module integration demos
- **Validation reports** — Config and link check results

## Agent Instructions

1. **Reference first** — Check examples before implementing new patterns
2. **Copy and adapt** — Use examples as starting points
3. **Update examples** — Keep examples in sync with API changes
4. **Test examples** — Examples should be runnable
5. **Document patterns** — Examples explain the "how"

## Common Patterns

```python
# Run an example
from codomyrmex.examples import run_example

run_example("llm_chat")  # Interactive example

# List available examples
from codomyrmex.examples import list_examples

for example in list_examples():
    print(f"{example.name}: {example.description}")

# Use example as template
from codomyrmex.examples import get_example_code

code = get_example_code("agentic_memory_basic")
# Adapt code to your needs
```

## Key Examples

| Example | Description |
|---------|-------------|
| `llm_chat` | Basic LLM chat interaction |
| `agentic_memory` | Memory persistence patterns |
| `multi_agent` | Multi-agent coordination |
| `rag_pipeline` | RAG with vector store |

## Testing Patterns

```python
# Verify examples are valid Python
import ast
from codomyrmex.examples import get_example_code

for example in list_examples():
    code = get_example_code(example.name)
    ast.parse(code)  # Should not raise
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Consult examples for implementation patterns, use examples as templates during BUILD phases

### Architect Agent
**Use Cases**: Architecture review of example patterns, integration example design, usage pattern documentation

### QATester Agent
**Use Cases**: Validate example correctness, verify examples are runnable, ensure examples stay in sync with API

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
