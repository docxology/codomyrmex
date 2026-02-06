# FPF Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Firewall-Proxy-Format pattern for secure AI interactions.

## Key Features

- **Firewall** — Input/output filtering
- **Proxy** — Request interception
- **Format** — Response formatting
- **Policies** — Security policies

## Quick Start

```python
from codomyrmex.fpf import Firewall, Proxy

firewall = Firewall()
firewall.add_rule("block_pii", patterns=[r"\d{3}-\d{2}-\d{4}"])

proxy = Proxy(firewall)
safe_input = proxy.filter_input(user_input)
safe_output = proxy.filter_output(model_response)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/fpf/](../../../src/codomyrmex/fpf/)
- **Parent**: [Modules](../README.md)
