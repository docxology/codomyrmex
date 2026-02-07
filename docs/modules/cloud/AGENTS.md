# Cloud Module — Agent Coordination

## Purpose

Cloud Services Module for Codomyrmex.

## Key Capabilities

- Cloud operations and management

## Agent Usage Patterns

```python
from codomyrmex.cloud import *

# Agent uses cloud capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/cloud/](../../../src/codomyrmex/cloud/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`EdgeProvider`** — Supported edge providers.
- **`EdgeRegion`** — Common edge regions.
- **`EdgeFunctionConfig`** — Configuration for an edge function.
- **`EdgeDeployment`** — An edge function deployment.
- **`EdgeClient`** — Abstract base class for edge provider clients.

### Submodules

- `aws` — Aws
- `azure` — Azure
- `coda_io` — Coda Io
- `common` — Common
- `gcp` — Gcp
- `infomaniak` — Infomaniak

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cloud -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
