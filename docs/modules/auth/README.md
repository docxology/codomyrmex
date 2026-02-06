# Auth Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Authentication and authorization with JWT, OAuth2, API keys, and role-based access control.

## Key Features

- **JWT** — Token generation and validation
- **OAuth2** — OAuth2 provider integration
- **API Keys** — Key-based authentication
- **RBAC** — Role-based access control

## Quick Start

```python
from codomyrmex.auth import JWTManager, require_auth

jwt = JWTManager(secret="your-secret")
token = jwt.create_token(user_id="123")

@require_auth
async def protected_endpoint():
    return {"message": "Authenticated!"}
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/auth/](../../../src/codomyrmex/auth/)
- **Parent**: [Modules](../README.md)
