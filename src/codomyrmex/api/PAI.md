# Personal AI Infrastructure — API Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The API module provides PAI integration for building REST APIs.

## PAI Capabilities

### API Development

Build REST APIs:

```python
from codomyrmex.api import APIRouter, APIApp

router = APIRouter(prefix="/v1")

@router.get("/users")
async def list_users():
    return {"users": [...]}

app = APIApp()
app.include_router(router)
```

### Middleware Support

Add middleware:

```python
from codomyrmex.api import APIApp, AuthMiddleware

app = APIApp()
app.add_middleware(AuthMiddleware())
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `APIRouter` | Define routes |
| `APIApp` | Application setup |
| `Middleware` | Request processing |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
