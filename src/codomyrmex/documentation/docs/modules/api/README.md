<!-- readme: generated -->

# api

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/api/`

## Overview

Unified API Module for Codomyrmex.

This module provides comprehensive API functionality including:
- API documentation generation and management
- API standardization (REST, GraphQL, versioning)
- OpenAPI specification generation
- Authentication (API key, bearer token, basic, HMAC)
- Rate limiting (fixed window, sliding window, token bucket)
- Circuit breaker, retry, and bulkhead patterns
- Webhook dispatch and management
- API mocking for testing
- Pagination (offset, cursor, keyset)

The module is organized into submodules:
- documentation: API documentation generation from code analysis
- standardization: REST/GraphQL API frameworks and versioning
- authentication: Multiple authentication mechanisms
- rate_limiting: Rate limiter implementations and middleware
- circuit_breaker: Resilience patterns (circuit breaker, retry, bulkhead)
- webhooks: Webhook event dispatch and registry
- mocking: Mock API server for testing
- pagination: Cursor, offset, and keyset pagination

## Submodules

| Submodule | Description |
|-----------|-------------|
| `rate_limiting:` | Consolidated rate limiting capabilities. |

## Public Exports

`api` exports 111 public symbols via `__all__`:

`RESTAPI`, `APIDocumentation`, `APIDocumentationGenerator`, `APIKeyAuthenticator`, `APIRequest`, `APIResponse`, `APIRouter`, `APISchema`, `APIVersion`, `APIVersionManager`, `AuthCredentials`, `AuthResult`, `AuthType`, `Authenticator`, `BasicAuthenticator`, `BearerTokenAuthenticator`, `Bulkhead`, `BulkheadFullError`, `CircuitBreaker`, `CircuitBreakerConfig`, `CircuitOpenError`, `CircuitState`, `CircuitStats`, `CompositeRateLimiter` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../api/](../../../../api/)
