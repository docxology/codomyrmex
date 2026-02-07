# Processing — Functional Specification

**Module**: `codomyrmex.video.processing`
**Status**: Active

## 1. Overview

Video processing submodule.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `VideoProcessor` | Class | Video processing class for manipulating video files. |

## 3. API Usage

```python
from codomyrmex.video.processing import VideoProcessor
```

## 4. Dependencies

See `src/codomyrmex/video/processing/__init__.py` for import dependencies.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k processing -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Video](../SPEC.md)
