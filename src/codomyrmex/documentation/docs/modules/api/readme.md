# API

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The API module provides comprehensive API infrastructure for building, documenting, securing, and testing APIs within the codomyrmex platform. It includes REST and GraphQL API frameworks, OpenAPI specification generation, multiple authentication mechanisms (API key, bearer token, basic, HMAC), rate limiting strategies (fixed window, sliding window, token bucket), resilience patterns (circuit breaker, retry, bulkhead), webhook dispatch, mock API servers for testing, and pagination implementations (offset, cursor, keyset). This module sits at the Core layer, consumed by Service and Application layer modules.

## Architecture Overview

The module is organized into eight self-contained subpackages, each providing a distinct API concern. All subpackages share common types via the root `__init__.py` and the `openapi_generator.py` shared component.

```
api/
├── __init__.py              # Unified public API (120+ exports)
├── openapi_generator.py     # Shared OpenAPI generator components
├── mcp_tools.py             # MCP tools (api_list_endpoints, api_get_spec, api_health_check)
├── documentation/           # API doc generation from code analysis
├── standardization/         # REST/GraphQL frameworks, versioning, OpenAPI generation
├── authentication/          # API key, bearer, basic, HMAC authenticators
├── rate_limiting/           # Fixed window, sliding window, token bucket, composite
├── circuit_breaker/         # Circuit breaker, retry, bulkhead patterns
├── webhooks/                # Webhook dispatch, registry, signature verification
├── mocking/                 # Mock API server, request matching, response fixtures
└── pagination/              # Offset, cursor, keyset pagination
```

## PAI Integration

### Algorithm Phase Mapping

| Algorithm Phase | Role | Key Operations |
|----------------|------|---------------|
| OBSERVE | Read API configurations and inspect endpoint definitions | `api_list_endpoints`, `api_health_check` |
| BUILD | Register endpoints, generate OpenAPI specs, configure auth | `api_get_spec`, direct Python import |
| EXECUTE | Make API calls, dispatch webhooks, handle requests | Direct Python import |

## Key Classes and Functions

### REST API Framework

**`RESTAPI`** -- REST API application with route registration and request handling.

```python
from codomyrmex.api import create_api, create_router

api = create_api(title="My Service", version="1.0.0")
router = create_router(prefix="/users")
api.add_router(router)
```

### GraphQL Framework

**`GraphQLAPI`** -- GraphQL API application with schema execution.

**`GraphQLSchema`** / **`GraphQLObjectType`** / **`GraphQLField`** -- Schema definition types.

### Authentication

**`APIKeyAuthenticator`** / **`BearerTokenAuthenticator`** / **`BasicAuthenticator`** / **`HMACAuthenticator`** -- Concrete authenticators implementing the `Authenticator` interface.

### Rate Limiting

**`FixedWindowLimiter`** / **`SlidingWindowLimiter`** / **`TokenBucketLimiter`** -- Rate limiter implementations.

**`CompositeRateLimiter`** -- Combines multiple rate limiting strategies.

### Resilience

**`CircuitBreaker`** -- Circuit breaker with configurable failure thresholds and recovery timeout.

**`RetryPolicy`** -- Configurable retry with exponential backoff.

**`Bulkhead`** -- Concurrency isolation to prevent cascade failures.

### Webhooks

**`WebhookDispatcher`** / **`WebhookRegistry`** -- Dispatch events and manage endpoint registrations.

### Pagination

**`OffsetPaginator`** / **`CursorPaginator`** / **`KeysetPaginator`** -- Pagination strategy implementations.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `api_list_endpoints` | List API endpoints discovered from source code | `source_path: str = "."` | Safe |
| `api_get_spec` | Generate an API specification from source code | `title: str`, `version: str`, `source_paths: str`, `base_url: str` | Safe |
| `api_health_check` | Check health/availability of API submodules | (none) | Safe |

## Usage Examples

### Example 1: REST API with Rate Limiting

```python
from codomyrmex.api import create_api, create_rate_limiter, CircuitBreaker

api = create_api(title="My Service", version="1.0.0")
limiter = create_rate_limiter(strategy="token_bucket", max_tokens=100, refill_rate=10)

result = limiter.check("client-ip-123")
print(f"Allowed: {result.allowed}, Remaining: {result.remaining}")
```

### Example 2: Circuit Breaker Pattern

```python
from codomyrmex.api import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
response = breaker.call(lambda: external_api.get("/data"))
```

## Error Handling

- `CircuitOpenError` -- Raised when calling through an open circuit breaker
- `BulkheadFullError` -- Raised when bulkhead concurrency limit is reached
- `RateLimitExceeded` -- Raised when rate limit is exceeded

## Related Modules

- [`security`](../security/readme.md) -- Security scanning and auditing for APIs
- [`validation`](../validation/readme.md) -- Schema and config validation
- [`networking`](../networking/readme.md) -- Network transport layer

## Navigation

- **Source**: [src/codomyrmex/api/](../../../../src/codomyrmex/api/)
- **API Spec**: [API_SPECIFICATION.md](../../../../src/codomyrmex/api/API_SPECIFICATION.md)
- **Parent**: [All Modules](../README.md)
