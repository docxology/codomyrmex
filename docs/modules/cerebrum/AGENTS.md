# Cerebrum Module — Agent Coordination

## Purpose

CEREBRUM Module for Codomyrmex.

## Key Capabilities

- Cerebrum operations and management

## Agent Usage Patterns

```python
from codomyrmex.cerebrum import *

# Agent uses cerebrum capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/cerebrum/](../../../src/codomyrmex/cerebrum/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`BaseNetworkVisualizer`** — Base class for network visualizations.
- **`BaseChartVisualizer`** — Base class for chart visualizations.
- **`ThemeColors`** — Theme color palette.
- **`ThemeFont`** — Theme font settings.
- **`Theme`** — Visualization theme manager.
- **`get_default_theme()`** — Get the default theme instance.

### Submodules

- `core` — Core
- `fpf` — FPF
- `inference` — Inference
- `visualization` — Visualization

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cerebrum -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
