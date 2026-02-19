# Security AI Safety Submodule

**Version**: v0.1.7 | **Source**: [`src/codomyrmex/security/ai_safety/`](../../../../src/codomyrmex/security/ai_safety/)

## Overview

AI-specific security capabilities including jailbreak detection, adversarial containment, prompt injection defense, and AI safety monitoring. Wraps and extends the defense module capabilities with a unified `AISafetyMonitor` interface.

## Components

| Source File | Classes / Functions | Availability Flag |
|-------------|--------------------|--------------------|
| `__init__.py` | `AISafetyMonitor`, `check_input()`, `get_incident_report()` | Always available |
| (optional) `defense.active` | `ActiveDefense` | `ACTIVE_DEFENSE_AVAILABLE` |
| (optional) `defense.rabbithole` | `RabbitHole` | `RABBITHOLE_AVAILABLE` |

## Exports (via top-level `security/__init__.py`)

When `AI_SAFETY_AVAILABLE` is `True`, the following symbol is re-exported:
- `AISafetyMonitor`

## Key Methods

| Method | Description |
|--------|-------------|
| `AISafetyMonitor.check_input()` | Check input text for AI safety violations, returns safe/threats/action dict |
| `AISafetyMonitor.get_incident_report()` | Get summary of detected incidents (last 10) |

## Navigation

- **Parent**: [Security Module](../README.md)
- **Source**: [`src/codomyrmex/security/ai_safety/`](../../../../src/codomyrmex/security/ai_safety/)
- **Conceptual Guide**: [AI Safety Concepts](../../../security/ai-safety.md)
