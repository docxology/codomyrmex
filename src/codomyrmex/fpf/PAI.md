# Personal AI Infrastructure — FPF Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The FPF module provides PAI integration for Firewall-Proxy-Format security patterns.

## PAI Capabilities

### Input Filtering

Filter AI inputs:

```python
from codomyrmex.fpf import Firewall

firewall = Firewall()
firewall.add_rule("block_pii", patterns=[r"\d{3}-\d{2}-\d{4}"])
safe = firewall.filter(user_input)
```

### Output Formatting

Format AI outputs:

```python
from codomyrmex.fpf import Formatter

formatter = Formatter()
formatted = formatter.apply(ai_response, format="json")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `Firewall` | Filter inputs |
| `Proxy` | Intercept requests |
| `Formatter` | Format outputs |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
