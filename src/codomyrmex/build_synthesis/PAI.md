# Personal AI Infrastructure — Build Synthesis Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Build Synthesis module provides PAI integration for project scaffolding.

## PAI Capabilities

### Project Scaffolding

Create new projects:

```python
from codomyrmex.build_synthesis import Scaffolder

scaffolder = Scaffolder()
scaffolder.create_project(
    name="my_app",
    template="fastapi",
    directory="./projects/"
)
```

### Code Generation

Generate code files:

```python
from codomyrmex.build_synthesis import FileGenerator

generator = FileGenerator()
generator.create_file("src/main.py", template="main")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Scaffolder` | New projects |
| `FileGenerator` | Generate files |
| `Template` | Templates |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
