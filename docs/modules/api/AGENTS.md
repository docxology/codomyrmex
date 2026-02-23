# Agent Guidelines - API

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

RESTful API framework with routing, middleware, and OpenAPI support.

## Key Classes

- **APIRouter** — Route definitions
- **APIApp** — Application instance
- **Request/Response** — HTTP objects
- **Middleware** — Request processing

## Agent Instructions

1. **Version APIs** — /v1/, /v2/ prefixes
2. **Use middleware** — Auth, logging, validation
3. **Document endpoints** — OpenAPI/Swagger
4. **Handle errors** — Consistent error format
5. **Validate input** — Use Pydantic models

## Common Patterns

```python
from codomyrmex.api import APIRouter, APIApp, JSONResponse

router = APIRouter(prefix="/v1")

@router.get("/users")
async def list_users():
    return JSONResponse(users)

@router.post("/users")
async def create_user(request):
    data = await request.json()
    user = create(data)
    return JSONResponse(user, status=201)

# Create app
app = APIApp()
app.include_router(router)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
```

## Testing Patterns

```python
from codomyrmex.api.testing import TestClient

client = TestClient(app)

# Test endpoint
response = client.get("/v1/users")
assert response.status_code == 200

# Test with auth
response = client.post("/v1/users", 
    json={"name": "Test"},
    headers={"Authorization": "Bearer token"}
)
assert response.status_code == 201
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
