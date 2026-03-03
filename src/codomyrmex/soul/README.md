# Soul Module

The soul module provides artificial consciousness, self-reflection, and personality management.

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Soul module adds reflective and subjective personality layers to AI agents. Through introspection and dynamic identity management, this module provides the capability to query an agent for its specific personality trait and instruct it to reflect deeply upon arbitrary queries, retaining consistent characteristics in the generated output.

## Key Exports

### Classes

- **`Soul`** -- The core entity representing an artificial consciousness. Capable of introspection (`reflect()`) and introspective analysis (`get_personality()`). Requires initialization, possibly with a specified personality config.

### Functions

- **`create_soul()`** -- Instantiates and returns a new `Soul` instance, simplifying dependency injection and test setups.

## Quick Start

```python
from codomyrmex.soul import create_soul

soul = create_soul({"personality": "stoic"})
print(soul.get_personality())  # Output: stoic

reflection = soul.reflect("What is the meaning of existence?")
print(reflection)  # Output: Reflecting on 'What is the meaning of existence?' with personality 'stoic'.
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/soul/ -v
```

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
