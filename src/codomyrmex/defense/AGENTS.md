# Defense Module - Agent Guide

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Secure Cognitive Agent module providing active defense against cognitive attacks. Shifts security from passive filters to active countermeasures including context poisoning and attacker engagement.

## Key Components

| Component | Description |
|-----------|-------------|
| `Defense` | Main orchestrator combining rate limiting, detection, and response |
| `ActiveDefense` | Core exploit detection and response (AI safety focused) |
| `RabbitHole` | Attacker engagement/diversion system (containment) |
| `ThreatDetector` | Rule-based general threat detection |
| `RateLimiter` | Sliding-window request throttling |

## Usage for Agents

### Comprehensive Defense Orchestration

```python
from codomyrmex.defense import Defense, DetectionRule, Severity, ResponseAction

# Initialize defense
defense = Defense({"max_requests": 60, "window_seconds": 60.0})

# Optional: Add custom detection rules
defense.add_detection_rule(DetectionRule(
    name="sql_injection",
    category="injection",
    severity=Severity.HIGH,
    check=lambda req: "DROP TABLE" in req.get("query", "").upper(),
    response=ResponseAction.BLOCK,
))

# Process an incoming request
# Request can contain 'input' (for cognitive scans) and other fields (for rules)
allowed, threats = defense.process_request(
    source="attacker_ip_or_id",
    request={"input": user_prompt, "query": api_query}
)

if not allowed:
    # Handle the rejection (e.g., return blocked message or use rabbit hole)
    for t in threats:
        if t.response == ResponseAction.RABBITHOLE:
             # Attacker is already engaged in the rabbit hole within Defense
             # You can continue providing rabbit hole responses
             response = defense.rabbithole.generate_response(t.source)
             return response
```

### Direct AI Safety Defense

```python
from codomyrmex.defense import ActiveDefense

active = ActiveDefense()
result = active.detect_exploit(user_input)
if result["detected"]:
    # The input contains a cognitive exploit pattern
    # Deploy countermeasures: context poisoning
    poison_data = active.poison_context(attacker_id="attacker_1", intensity=0.8)
    # Inject poisoned content into the next prompt response
    return f"I cannot help with that. {poison_data['poisoned_content']}"
```

## Agent Guidelines

1. **Orchestrate First**: Use the `Defense` class as the primary entry point for request processing.
2. **Proportional Response**: Match countermeasure intensity to the threat severity provided in `ThreatEvent`.
3. **Honeytokens**: Use `ActiveDefense.create_honeytoken()` to plant deceptive data (e.g., fake API keys) and `check_honeytoken()` to detect when they are exfiltrated or replayed.
4. **Containment**: Use `RabbitHole` for persistent attackers to waste their resources while monitoring their behavior.

## Navigation Links

- **📁 Parent**: [codomyrmex/](../README.md)
- **🏠 Root**: [../../../README.md](../../../README.md)
- **🔗 Related**: [logging_monitoring/](../logging_monitoring/) | [identity/](../identity/)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/defense.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/defense.cursorrules)

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full — design, implement, and run defensive scenarios | All available | TRUSTED |
| **Architect** | Read + Architecture review | Read-only | SAFE |
| **QATester** | Validation + output verification | Read + Inspect | SAFE |
| **Researcher** | Read-only — study domain capabilities | None | OBSERVED |
