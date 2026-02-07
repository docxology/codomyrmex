# Build Synthesis Module — Agent Coordination

## Purpose

Build Synthesis Module for Codomyrmex.

## Key Capabilities

- Build Synthesis operations and management

## Agent Usage Patterns

```python
from codomyrmex.build_synthesis import *

# Agent uses build synthesis capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/build_synthesis/](../../../src/codomyrmex/build_synthesis/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`BuildType`** — Types of builds supported.
- **`BuildStatus`** — Build status states.
- **`BuildEnvironment`** — Build environments.
- **`DependencyType`** — Types of dependencies.
- **`BuildStep`** — Individual build step definition.
- **`create_python_build_target()`** — Create a Python build target.
- **`create_docker_build_target()`** — Create a Docker build target.
- **`create_static_build_target()`** — Create a static site build target.
- **`get_available_build_types()`** — Get list of available build types.
- **`get_available_environments()`** — Get list of available build environments.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k build_synthesis -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
