# Build Synthesis Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Automated build pipeline synthesis including dependency resolution, compilation orchestration, and artifact generation.

## Key Features

- **BuildType** — Types of builds supported.
- **BuildStatus** — Build status states.
- **BuildEnvironment** — Build environments.
- **DependencyType** — Types of dependencies.
- **BuildStep** — Individual build step definition.
- **BuildTarget** — Build target definition.
- `create_python_build_target()` — Create a Python build target.
- `create_docker_build_target()` — Create a Docker build target.
- `create_static_build_target()` — Create a static site build target.
- `get_available_build_types()` — Get list of available build types.

## Quick Start

```python
from codomyrmex.build_synthesis import BuildType, BuildStatus, BuildEnvironment

instance = BuildType()
```

## Source Files

- `build_manager.py`
- `build_orchestrator.py`

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k build_synthesis -v
```

## Navigation

- **Source**: [src/codomyrmex/build_synthesis/](../../../src/codomyrmex/build_synthesis/)
- **Parent**: [Modules](../README.md)
