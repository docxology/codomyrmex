# Containerization Module — Agent Coordination

## Purpose

Containerization Module for Codomyrmex.

## Key Capabilities

- Containerization operations and management

## Agent Usage Patterns

```python
from codomyrmex.containerization import *

# Agent uses containerization capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/containerization/](../../../src/codomyrmex/containerization/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`ContainerError`** — Base exception for container-related errors.
- **`ImageBuildError`** — Raised when container image build operations fail.
- **`NetworkError`** — Raised when container network operations fail.
- **`VolumeError`** — Raised when container volume operations fail.
- **`RegistryError`** — Raised when container registry operations fail.

### Submodules

- `docker` — Docker
- `kubernetes` — Kubernetes
- `registry` — Registry
- `security` — Security

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k containerization -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
