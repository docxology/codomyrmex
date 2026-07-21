# Defense API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Public Classes

| Symbol | Purpose |
| :--- | :--- |
| `ActiveDefense` | Prompt-exploit detection, context poisoning, honeytokens, and metrics |
| `RabbitHole` | Containment session tracker with decoy responses |
| `Defense` | Request-processing orchestrator |
| `RateLimiter` | Sliding-window rate limiter |
| `ThreatDetector` | Detection-rule evaluator |
| `DetectionRule` | Rule dataclass with name, category, severity, check, description, and response |
| `ThreatEvent` | Event dataclass emitted by request processing |

## Enums

- `ThreatLevel`: `NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `Severity`: `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `ResponseAction`: `LOG`, `THROTTLE`, `BLOCK`, `ALERT`, `QUARANTINE`, `RABBITHOLE`, `POISON`

## Primary Methods

| Method | Returns |
| :--- | :--- |
| `ActiveDefense.detect_exploit(text)` | `dict` with `detected`, `patterns`, and `threat_level` |
| `ActiveDefense.poison_context(attacker_id, intensity)` | `dict` with attacker id, generated content, intensity, and timestamp |
| `ActiveDefense.create_honeytoken(label)` | Honeytoken string |
| `ActiveDefense.check_honeytoken(text)` | Triggered token list |
| `ActiveDefense.get_threat_report()` | Metrics dictionary |
| `Defense.process_request(source, request)` | `(allowed, threats)` tuple |
| `Defense.add_detection_rule(rule)` | `None` |
| `Defense.block_source(source)` / `unblock_source(source)` | `None` |

## Factory

`create_defense(config=None)` returns a `Defense` instance.

## Validation

- Source tests: `uv run pytest tests/unit/defense/ -q`
- API import check: `python -c "from codomyrmex.defense import Defense, ActiveDefense"`
