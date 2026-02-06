# Personal AI Infrastructure — Rate Limiting Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Rate Limiting module provides PAI integration for request throttling, enabling AI agents to respectfully interact with external services.

## PAI Capabilities

### API Request Management

Control AI agent request rates:

```python
from codomyrmex.rate_limiting import (
    RateLimiter, TokenBucketLimiter, QuotaManager
)

# Create limiter for API calls
limiter = TokenBucketLimiter(
    rate=10,      # 10 requests
    period=60,    # per minute
    burst=3       # allow burst of 3
)

# Check before making requests
if limiter.allow("openai_api"):
    response = make_api_call()
else:
    wait_time = limiter.time_until_allowed("openai_api")
    print(f"Rate limited. Wait {wait_time}s")
```

### Quota Tracking

Track usage across multiple resources:

```python
from codomyrmex.rate_limiting import QuotaManager

# Manage quotas
quotas = QuotaManager()
quotas.set_quota("tokens", daily_limit=100000)

# Track usage
quotas.use("tokens", amount=1500)
remaining = quotas.get_remaining("tokens")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `RateLimiter` | Control request rates |
| `QuotaManager` | Track resource usage |
| `TokenBucketLimiter` | Handle burst traffic |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
