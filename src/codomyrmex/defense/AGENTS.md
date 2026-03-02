# Defense Module - Agent Guide

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, threat model design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, defensive control validation | OBSERVED |

### Engineer Agent
**Use Cases**: Implement security defenses, configure exploit detection, deploy countermeasures during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Review threat models, validate defense-in-depth architecture, design countermeasure escalation strategies

### QATester Agent
**Use Cases**: Validate defensive controls under simulated attacks, verify exploit detection accuracy, test proportional response logic

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [identity/](../identity/) | [wallet/](../wallet/) | [privacy/](../privacy/)
