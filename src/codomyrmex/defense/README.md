# Defense Module

**Version**: v0.1.0 | **Status**: Active

Active countermeasures and threat containment for AI security.

## Quick Start

```python
from codomyrmex.defense import ActiveDefense, RabbitHole

# Active defense with threat response
defense = ActiveDefense()

# Register threat handlers
defense.on_threat("injection", handler=quarantine_input)
defense.on_threat("exfiltration", handler=block_request)

# Check and respond to threats
if defense.detect(user_input):
    defense.respond()

# Rabbit hole containment
hole = RabbitHole()
hole.enter(suspicious_agent)  # Isolate in sandboxed environment
hole.monitor()  # Track behavior
hole.release() if safe else hole.terminate()
```

## Exports

| Class | Description |
|-------|-------------|
| `ActiveDefense` | Threat detection and automated response |
| `RabbitHole` | Deceptive containment environment |

## Use Cases

- **Injection detection** — Detect and block prompt injection attempts
- **Agent containment** — Isolate suspicious agents in sandboxed environments
- **Threat response** — Automated countermeasures for detected threats

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
