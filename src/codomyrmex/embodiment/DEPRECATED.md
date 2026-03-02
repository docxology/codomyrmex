# DEPRECATED — `embodiment` Module

**Status**: Deprecated since v1.0.0 | **Planned Removal**: v2.0.0

## Reason

The `embodiment` module has zero intersection with the Codomyrmex coding platform mission. It was an experimental prototype for physical embodiment interfaces (ROS2, sensor management) that is no longer maintained.

## Migration Guide

**There is no replacement module.** This module has no active consumers within Codomyrmex.

If you are importing from `codomyrmex.embodiment`:

```python
# ❌ Deprecated — will emit DeprecationWarning
from codomyrmex.embodiment import EmbodimentInterface

# ✅ No direct replacement — remove usage
# If ROS2 integration is needed, use rclpy directly
```

## Current State

- All imports still work (backward-compatible)
- `DeprecationWarning` emitted on import
- No further development planned
- No tests reference this module

## Timeline

| Version | Action |
| :--- | :--- |
| v1.0.0 | Deprecated with `DeprecationWarning` |
| v1.1.0 | No changes planned |
| v2.0.0 | Scheduled for removal |

## See Also

- [README.md](README.md) — Module overview
- [AGENTS.md](AGENTS.md) — Agent coordination
- [TO-DO.md](../../../TO-DO.md) — Longer-term vision section
