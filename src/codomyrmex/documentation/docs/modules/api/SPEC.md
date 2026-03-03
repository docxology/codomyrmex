# API -- Technical Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: REST API Framework
- The system shall provide a `RESTAPI` class for route registration, request handling, and middleware support.
- Routers shall support prefix-based grouping with shared middleware.
- Endpoints shall support all standard HTTP methods (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS).

### FR-2: GraphQL Framework
- The system shall provide a `GraphQLAPI` class with schema-based query and mutation execution.
- Schema definition shall support object types, fields, resolvers, and mutations.

### FR-3: API Versioning
- `APIVersionManager` shall manage multiple API versions and route requests to the appropriate version handler.
- Versions shall support deprecation marking.

### FR-4: Authentication
- The system shall provide four authenticator implementations: API Key, Bearer Token, Basic Auth, and HMAC.
- All authenticators shall implement the `Authenticator` interface returning `AuthResult`.
- `create_authenticator()` factory shall create authenticators by `AuthType` enum.

### FR-5: Rate Limiting
- The system shall provide three rate limiting algorithms: fixed window, sliding window, and token bucket.
- `CompositeRateLimiter` shall combine multiple strategies.
- `RateLimiterMiddleware` shall integrate with request pipelines.

### FR-6: Resilience Patterns
- `CircuitBreaker` shall track failure counts and open/close based on configurable thresholds.
- `RetryPolicy` shall support configurable retry counts with exponential backoff.
- `Bulkhead` shall limit concurrent executions to prevent cascade failures.

### FR-7: Webhooks
- `WebhookRegistry` shall manage endpoint registrations and event subscriptions.
- `WebhookDispatcher` shall dispatch events with retry and signature verification.

### FR-8: API Mocking
- `MockAPIServer` shall provide an in-process mock server with configurable routes.
- `RequestMatcher` shall support pattern-based request matching.

### FR-9: Pagination
- The system shall provide three pagination strategies: offset, cursor, and keyset.
- All paginators shall implement the `Paginator` interface.

## Interface Contracts

### MCP Tool Signatures

```python
def api_list_endpoints(source_path: str = ".") -> dict[str, Any]
def api_get_spec(title: str = "Codomyrmex API", version: str = "1.0.0",
                 source_paths: str = "", base_url: str = "") -> dict[str, Any]
def api_health_check() -> dict[str, Any]
```

## Non-Functional Requirements

### NFR-1: Performance
- Rate limiter check operations shall complete in O(1) time.
- Circuit breaker state transitions shall be atomic and thread-safe.

### NFR-2: Extensibility
- New authentication schemes shall be addable by implementing the `Authenticator` interface.
- New rate limiting strategies shall be addable by extending `RateLimiterBase`.

## Testing Requirements

- All tests follow the Zero-Mock policy.
- Rate limiters tested with real time-based assertions.
- Circuit breaker tested with real failure injection.
- Mock server tested as an actual in-process server, not mocked.

## Navigation

- **Source**: [src/codomyrmex/api/](../../../../src/codomyrmex/api/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
