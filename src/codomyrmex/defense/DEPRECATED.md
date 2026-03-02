# DEPRECATED — `defense` Module

**Status**: Deprecated since v1.0.0 | **Migration Target**: `security.ai_safety`

## Reason

The `defense` module is being restructured into `codomyrmex.security.ai_safety`. The active defense and rabbit hole containment capabilities are more appropriately housed within the security architecture.

## Migration Guide

```python
# ❌ Deprecated — will emit DeprecationWarning
from codomyrmex.defense import ActiveDefense, RabbitHole

# ✅ Use the security.ai_safety module instead
from codomyrmex.security.ai_safety import ActiveDefense, RabbitHole
```

### API Compatibility

The `security.ai_safety` module provides the same public API:

| Old Import | New Import |
| :--- | :--- |
| `defense.ActiveDefense` | `security.ai_safety.ActiveDefense` |
| `defense.RabbitHole` | `security.ai_safety.RabbitHole` |
| `defense.detect_exploit()` | `security.ai_safety.detect_exploit()` |
| `defense.analyze_context_poisoning()` | `security.ai_safety.analyze_context_poisoning()` |

## Current State

- All imports still work (backward-compatible shim)
- `DeprecationWarning` emitted on import
- `security.ai_safety` is the active module
- Tests should import from `security.ai_safety`

## Timeline

| Version | Action |
| :--- | :--- |
| v1.0.0 | Deprecated with migration shim |
| v1.1.0 | Shim remains; documentation updated |
| v2.0.0 | Shim removed; direct imports fail |

## See Also

- [README.md](README.md) — Module overview
- [security/ai_safety/README.md](../security/ai_safety/README.md) — Migration target
- [TODO.md](../../../TODO.md) — Structural quality items
