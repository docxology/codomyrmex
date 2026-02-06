# Personal AI Infrastructure — Utils Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Utils module provides PAI integration for common utility functions.

## PAI Capabilities

### Common Utilities

Useful helper functions:

```python
from codomyrmex.utils import retry, slugify, ensure_dir

@retry(max_attempts=3, backoff=2.0)
def flaky_api_call():
    return call_api()

slug = slugify("Hello World!")  # "hello-world"
ensure_dir("./output/data/")
```

### File Utilities

File operations:

```python
from codomyrmex.utils import read_json, write_json

data = read_json("config.json")
write_json("output.json", result)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `retry` | Retry operations |
| `slugify` | Text processing |
| `file utilities` | File operations |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
