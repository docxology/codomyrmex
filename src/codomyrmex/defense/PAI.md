# Personal AI Infrastructure — Defense Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Defense module provides active countermeasures and "Rabbit Hole" containment for AI safety. It detects and mitigates adversarial prompts, infinite loops, and resource exhaustion attacks targeting AI agents. Part of the Secure Cognitive Agent suite.

> [!NOTE]
> This module is deprecated in favor of `security.ai_safety`. Imports are forwarded for backward compatibility.

## PAI Capabilities

### Active Defense

```python
from codomyrmex.defense import ActiveDefense

defense = ActiveDefense()
# Monitor agent behavior for anomalies
# Detect adversarial prompt injection attempts
# Enforce resource limits on agent execution
```

### Rabbit Hole Containment

```python
from codomyrmex.defense import RabbitHole

containment = RabbitHole()
# Detect when agents enter infinite reasoning loops
# Automatically break out of unproductive cycles
# Log containment events for post-mortem analysis
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ActiveDefense` | Class | Adversarial detection and active countermeasures |
| `RabbitHole` | Class | Infinite loop detection and cycle-breaking containment |

## PAI Algorithm Phase Mapping

| Phase | Defense Contribution |
|-------|----------------------|
| **EXECUTE** | Monitor agent execution for adversarial behavior; enforce resource limits |
| **VERIFY** | Validate that agent actions are within safety boundaries |
| **LEARN** | Log containment events and defense activations for improving safety |

## Architecture Role

**Specialized Layer** — Part of the Secure Cognitive Agent suite (`identity`, `wallet`, `defense`, `market`, `privacy`). Being migrated to `security.ai_safety`.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.defense import ...`
- CLI: `codomyrmex defense <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
