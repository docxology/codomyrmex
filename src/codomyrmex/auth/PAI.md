# Personal AI Infrastructure — Auth Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Auth module provides PAI integration for authentication and authorization.

## PAI Capabilities

### Token Management

Manage authentication tokens:

```python
from codomyrmex.auth import JWTManager

jwt = JWTManager(secret="your-secret")
token = jwt.create_token(user_id="123", roles=["admin"])

claims = jwt.verify_token(token)
```

### API Key Authentication

Manage API keys:

```python
from codomyrmex.auth import APIKeyManager

keys = APIKeyManager()
key = keys.create(name="development", scopes=["read"])

is_valid = keys.validate(api_key)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `JWTManager` | Token management |
| `APIKeyManager` | API key auth |
| `RBACManager` | Role-based access |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
