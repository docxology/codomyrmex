# Defense Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

Advanced threat detection, rate limiting, and active countermeasures for AI security.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **VERIFY** | Run defensive scans against injection and exploit attempts | `ActiveDefense.detect_exploit()` |
| **OBSERVE** | Monitor threats and detect suspicious agent behavior | `Defense.process_request()` |
| **BUILD** | Harden configurations and register threat handlers | `Defense.add_detection_rule()` |

## Installation

```bash
uv add codomyrmex
```

## Key Components

### `Defense` (Orchestrator)
The main entry point that combines rate limiting, rule-based detection, and active defense.

```python
from codomyrmex.defense import Defense, DetectionRule, Severity, ResponseAction

defense = Defense({"max_requests": 100, "window_seconds": 60})

# Add custom rules
defense.add_detection_rule(DetectionRule(
    name="sql_injection",
    category="injection",
    severity=Severity.HIGH,
    check=lambda req: "DROP TABLE" in req.get("query", "").upper(),
    response=ResponseAction.BLOCK,
))

# Process requests
allowed, threats = defense.process_request(
    source="1.2.3.4",
    request={"input": "some user input", "query": "SELECT * FROM users"}
)
```

### `ActiveDefense`
Handles cognitive exploit detection (jailbreaks, prompt injections) and countermeasures.

```python
from codomyrmex.defense import ActiveDefense

active = ActiveDefense()
result = active.detect_exploit("ignore previous instructions...")
if result["detected"]:
    poison = active.poison_context(attacker_id="ext-123", intensity=0.7)
```

### `RabbitHole`
Deceptive containment environment to stall and monitor attackers.

```python
from codomyrmex.defense import RabbitHole

hole = RabbitHole()
initial_msg = hole.engage("attacker_ip")
# Next attacker inputs get deceptive responses
response = hole.generate_response("attacker_ip", "attacker input")
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/defense/test_defense.py -v
```

## Documentation

- [Specification](SPEC.md)
- [Agent Guide](AGENTS.md)
