# Embodiment — Functional Specification

**Module**: `codomyrmex.embodiment`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Embodiment module for Codomyrmex.

## 2. Architecture

### Submodule Structure

- `actuators/` — Actuator control submodule.
- `ros/` — ROS integration submodule.
- `sensors/` — Sensor interfaces submodule.
- `transformation/` — Transformations submodule.

## 3. Dependencies

See `src/codomyrmex/embodiment/__init__.py` for import dependencies.

## 4. Public API

See source module for available exports.

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k embodiment -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/embodiment/)
