# defense - API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Public API

| Symbol | Type | Purpose |
| :--- | :--- | :--- |
| `ActiveDefense` | Class | Prompt-exploit detection, honeytokens, and threat reports |
| `RabbitHole` | Class | Source containment and decoy responses |
| `Defense` | Class | Request defense orchestrator |
| `RateLimiter` | Class | Sliding-window request limiter |
| `ThreatDetector` | Class | Detection-rule evaluation |
| `ThreatEvent` | Class | Structured threat finding |
| `DetectionRule` | Class | Rule definition for threat detection |
| `create_defense` | Function | Convenience factory |

## Example

```python
from codomyrmex.defense import DetectionRule, Defense

defense = Defense()
defense.add_rule(DetectionRule("override", "ignore previous", severity="high"))
allowed, threats = defense.process_request("source-1", {"input": "hello"})
```
