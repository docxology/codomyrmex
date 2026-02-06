# API Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

RESTful API framework with routing, middleware, OpenAPI support, and request/response handling.

## Key Features

- **Routing** — Decorators for GET, POST, PUT, DELETE endpoints
- **Middleware** — Authentication, logging, validation
- **OpenAPI** — Auto-generated API documentation
- **Async** — Full async/await support

## Quick Start

```python
from codomyrmex.api import APIRouter, APIApp

router = APIRouter(prefix="/v1")

@router.get("/users")
async def list_users():
    return {"users": [...]}

app = APIApp()
app.include_router(router)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/api/](../../../src/codomyrmex/api/)
- **Parent**: [Modules](../README.md)
