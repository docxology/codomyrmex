# Extraction — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.video.extraction`
**Status**: Active

## 1. Overview

Video extraction submodule.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `FrameExtractor` | Class | Extract frames and audio from video files. |

## 3. API Usage

```python
from codomyrmex.video.extraction import FrameExtractor
```

## 4. Dependencies

See `src/codomyrmex/video/extraction/__init__.py` for import dependencies.

## 5. Testing

```bash
uv run python -m pytest tests/ -k extraction -v
```

## References

- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [Parent: Video](../SPEC.md)

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
