# Build Synthesis Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Code generation, scaffolding, and project synthesis.

## Key Features

- **Scaffold** — Project templates
- **Generation** — Code generation
- **Templates** — File templates
- **Synthesis** — Full project setup

## Quick Start

```python
from codomyrmex.build_synthesis import Scaffolder

scaffolder = Scaffolder()
scaffolder.create_project(
    name="my_app",
    template="fastapi",
    directory="./projects/"
)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/build_synthesis/](../../../src/codomyrmex/build_synthesis/)
- **Parent**: [Modules](../README.md)
