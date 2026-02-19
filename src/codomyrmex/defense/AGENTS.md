# Defense Module - Agent Guide

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Secure Cognitive Agent module providing active defense against cognitive attacks. Shifts security from passive filters to active countermeasures including context poisoning and attacker engagement.

## Key Components

| Component | Description |
|-----------|-------------|
| `ActiveDefense` | Core exploit detection and response |
| `RabbitHole` | Attacker engagement/diversion system |
| `ContextPoisoner` | Injects false context to mislead attackers |
| `ExploitDetector` | Pattern-based attack detection |

## Usage for Agents

### Active Defense

```python
from codomyrmex.defense import ActiveDefense

defense = ActiveDefense()
if defense.detect_exploit(user_input):
    # Deploy countermeasures
    context = defense.poison_context(attacker_id="unknown", intensity=0.8)
    return context
```

### Rabbit Hole

```python
from codomyrmex.defense import RabbitHole

hole = RabbitHole()
# Engage attacker in endless loop
response = hole.engage("attacker_ip")
```

## Agent Guidelines

1. **Detection First**: Always detect before responding
2. **Proportional Response**: Match countermeasure to threat level
3. **Logging**: Log all defense activations for audit

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [identity/](../identity/) | [wallet/](../wallet/) | [privacy/](../privacy/)
