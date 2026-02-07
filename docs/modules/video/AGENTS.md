# Video Module — Agent Coordination

## Purpose

Video processing module for Codomyrmex.

## Key Capabilities

- Video operations and management

## Agent Usage Patterns

```python
from codomyrmex.video import *

# Agent uses video capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/video/](../../../src/codomyrmex/video/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`VideoConfig`** — Global configuration for video processing.
- **`VideoError`** — Base exception for all video-related errors.
- **`VideoReadError`** — Raised when reading a video file fails.
- **`VideoWriteError`** — Raised when writing a video file fails.
- **`VideoProcessingError`** — Raised when a video processing operation fails.
- **`get_config()`** — Get the global video configuration.
- **`set_config()`** — Set the global video configuration.
- **`reset_config()`** — Reset configuration to defaults.
- **`configure()`** — Configure video processing settings.

### Submodules

- `analysis` — Analysis
- `extraction` — Extraction
- `processing` — Processing

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k video -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
