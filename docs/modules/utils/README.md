# Utils Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Common utility functions, helpers, and shared utilities.

## Key Features

- **File Utils** — Path handling, file ops
- **String Utils** — Text manipulation
- **Date Utils** — Date/time helpers
- **Retries** — Retry decorators

## Quick Start

```python
from codomyrmex.utils import retry, slugify, ensure_dir

@retry(max_attempts=3)
def flaky_operation():
    return call_api()

slug = slugify("Hello World!")  # "hello-world"
ensure_dir("./output/data/")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/utils/](../../../src/codomyrmex/utils/)
- **Parent**: [Modules](../README.md)
