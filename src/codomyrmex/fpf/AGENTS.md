# Agent Guidelines - FPF

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Firewall-Proxy-Format pattern for secure AI interactions.

## Key Classes

- **Firewall** — Input/output filtering
- **Proxy** — Request interception
- **Formatter** — Response formatting
- **PolicyEngine** — Policy enforcement

## Agent Instructions

1. **Filter input** — Validate all incoming data
2. **Filter output** — Sanitize all responses
3. **Log intercepts** — Track blocked requests
4. **Update policies** — Keep rules current
5. **Whitelist approach** — Allow known-good only

## Common Patterns

```python
from codomyrmex.fpf import Firewall, Proxy, Formatter, PolicyEngine

# Configure firewall
firewall = Firewall()
firewall.add_rule("block_pii", patterns=["\\d{3}-\\d{2}-\\d{4}"])
firewall.add_rule("block_injection", patterns=["<script>"])

# Proxy for interception
proxy = Proxy(firewall)
safe_input = proxy.filter_input(user_input)
safe_output = proxy.filter_output(model_response)

# Format responses
formatter = Formatter()
response = formatter.format(result, template="markdown")

# Policy engine
policy = PolicyEngine()
policy.load("security_policies.yaml")
if not policy.allows("action", context):
    raise PolicyViolation()
```

## Testing Patterns

```python
# Verify firewall
firewall = Firewall()
firewall.add_rule("test", patterns=["blocked"])
result = firewall.filter("contains blocked word")
assert "blocked" not in result

# Verify proxy
proxy = Proxy(firewall)
safe = proxy.filter_input("<script>alert()</script>")
assert "<script>" not in safe
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
