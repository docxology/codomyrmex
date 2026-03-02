# Codomyrmex Agents — src/codomyrmex/security/ai_safety

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Unified AI safety monitoring that combines jailbreak detection, prompt injection defense, and adversarial containment. Wraps optional `codomyrmex.defense` components (`ActiveDefense`, `RabbitHole`) behind a single `AISafetyMonitor` interface.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `AISafetyMonitor` | Unified monitor: `check_input()` screens text for threats, `get_incident_report()` returns last 10 incidents |
| `__init__.py` | `ActiveDefense` (optional) | Exploit detection via `detect_exploit()` from `codomyrmex.defense.active` |
| `__init__.py` | `RabbitHole` (optional) | Adversarial containment from `codomyrmex.defense.rabbithole` |

## Operating Contracts

- `AISafetyMonitor.check_input()` returns `{"safe": bool, "threats": list, "action": "allow"|"block"}` -- never raises on benign input.
- Optional dependencies are detected at import time via `ACTIVE_DEFENSE_AVAILABLE` and `RABBITHOLE_AVAILABLE` flags.
- When defense modules are unavailable, `check_input()` returns `safe=True` with empty threats (no silent failure, just reduced coverage).
- Incident history is capped at the last 10 entries in `get_incident_report()`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.defense.active` (optional), `codomyrmex.defense.rabbithole` (optional)
- **Used by**: PAI trust gateway, agent input validation pipelines

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
