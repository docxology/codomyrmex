# API Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive API infrastructure module providing everything needed to build, document, secure, and test APIs. Includes REST and GraphQL API frameworks, OpenAPI specification generation, multiple authentication mechanisms (API key, bearer token, basic, HMAC), rate limiting strategies (fixed window, sliding window, token bucket), resilience patterns (circuit breaker, retry, bulkhead), webhook dispatch, mock API servers for testing, and pagination implementations (offset, cursor, keyset).

## Key Exports

### Documentation and OpenAPI
- **`APIDocumentationGenerator`** -- Generates API documentation from code analysis and annotations
- **`generate_api_docs()`** -- Convenience function to generate documentation for a codebase
- **`extract_api_specs()`** -- Extracts API specifications from source code
- **`APIDocumentation`** -- Structured representation of API documentation
- **`DocumentationAPIEndpoint`** -- Endpoint definition within documentation context
- **`DocumentationOpenAPIGenerator`** -- Generates OpenAPI specs from documentation artifacts
- **`generate_openapi_spec_from_docs()`** -- Produces an OpenAPI spec from analyzed documentation
- **`validate_openapi_spec()`** -- Validates an OpenAPI specification for correctness
- **`APISchema`** -- Schema definition for API data types

### REST API Framework
- **`RESTAPI`** -- REST API application with route registration and request handling
- **`StandardizationAPIEndpoint`** -- Endpoint definition with method, path, and handler
- **`APIResponse`** -- Standardized response wrapper with status, data, and metadata
- **`APIRouter`** -- Groups related endpoints with shared prefix and middleware
- **`HTTPMethod`** -- Enum for HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
- **`HTTPStatus`** -- Enum for HTTP status codes
- **`APIRequest`** -- Structured request object with headers, params, and body
- **`create_api()`** / **`create_router()`** -- Factory functions for REST API and router instances

### GraphQL Framework
- **`GraphQLAPI`** -- GraphQL API application with schema execution
- **`GraphQLSchema`** / **`GraphQLObjectType`** / **`GraphQLField`** / **`GraphQLType`** -- Schema definition types
- **`GraphQLResolver`** / **`GraphQLMutation`** / **`GraphQLQuery`** -- Resolver and operation types
- **`resolver()`** / **`mutation()`** -- Decorators for resolver and mutation registration
- **`create_schema()`** / **`create_object_type()`** / **`create_field()`** -- Factory functions

### API Versioning
- **`APIVersionManager`** -- Manages multiple API versions and routes requests appropriately
- **`APIVersion`** / **`VersionedEndpoint`** / **`VersionFormat`** -- Version definitions and formats
- **`version()`** / **`deprecated_version()`** -- Decorators for version tagging
- **`create_version_manager()`** / **`create_versioned_endpoint()`** -- Factory functions

### OpenAPI Generation
- **`StandardizationOpenAPIGenerator`** -- Generates OpenAPI specs from REST/GraphQL API definitions
- **`OpenAPISpecification`** -- In-memory OpenAPI spec representation
- **`generate_openapi_spec_from_api()`** -- Generates spec from a running API instance
- **`create_openapi_from_rest_api()`** / **`create_openapi_from_graphql_api()`** -- Spec builders
- **`SharedAPISchema`** -- Shared schema component across generators

### Authentication
- **`Authenticator`** -- Base authenticator interface
- **`APIKeyAuthenticator`** / **`BearerTokenAuthenticator`** / **`BasicAuthenticator`** / **`HMACAuthenticator`** -- Concrete authenticators
- **`AuthType`** / **`AuthCredentials`** / **`AuthResult`** -- Authentication enums and data types
- **`create_authenticator()`** -- Factory for creating authenticators by type

### Rate Limiting
- **`FixedWindowLimiter`** / **`SlidingWindowLimiter`** / **`TokenBucketLimiter`** -- Rate limiter implementations
- **`CompositeRateLimiter`** -- Combines multiple rate limiting strategies
- **`RateLimiterMiddleware`** -- Middleware adapter for request pipelines
- **`RateLimitStrategy`** / **`RateLimitResult`** / **`RateLimiterBase`** -- Base types
- **`create_rate_limiter()`** -- Factory function

### Circuit Breaker and Resilience
- **`CircuitBreaker`** -- Circuit breaker with configurable thresholds and recovery
- **`RetryPolicy`** -- Configurable retry with backoff strategies
- **`Bulkhead`** -- Concurrency isolation to prevent cascade failures
- **`CircuitState`** / **`CircuitStats`** / **`CircuitBreakerConfig`** -- State and configuration types
- **`CircuitOpenError`** / **`BulkheadFullError`** -- Resilience-specific exceptions
- **`circuit_breaker_decorator()`** / **`retry()`** -- Decorators for functions

### Webhooks
- **`WebhookDispatcher`** -- Dispatches webhook events to registered endpoints with retry
- **`WebhookRegistry`** -- Manages webhook endpoint registrations and subscriptions
- **`WebhookSignature`** -- Signs and verifies webhook payloads for authenticity
- **`HTTPWebhookTransport`** / **`WebhookTransport`** -- Transport layer for webhook delivery
- **`WebhookEvent`** / **`WebhookConfig`** / **`DeliveryResult`** -- Event and configuration types
- **`WebhookEventType`** / **`WebhookStatus`** / **`SignatureAlgorithm`** -- Enums
- **`create_webhook_registry()`** / **`create_webhook_dispatcher()`** -- Factory functions

### Mocking
- **`MockAPIServer`** -- In-process mock API server for testing with configurable routes
- **`RequestMatcher`** -- Matches incoming requests against defined patterns
- **`ResponseFixture`** -- Predefined response templates for testing
- **`MockRequest`** / **`MockResponse`** / **`MockRoute`** / **`RequestLog`** -- Mock types
- **`MatchStrategy`** / **`MockResponseMode`** -- Matching and response enums
- **`create_mock_server()`** / **`create_fixture()`** -- Factory functions

### Pagination
- **`OffsetPaginator`** / **`CursorPaginator`** / **`KeysetPaginator`** -- Pagination implementations
- **`Paginator`** -- Base paginator interface
- **`PaginatedResponse`** / **`PaginationRequest`** / **`PageInfo`** -- Request/response types
- **`PaginationStrategy`** / **`SortDirection`** -- Enums
- **`create_paginator()`** -- Factory function

## Directory Contents

- `documentation/` -- API documentation generation and OpenAPI spec creation from docs
- `standardization/` -- REST API framework, GraphQL framework, versioning, and OpenAPI generation
- `authentication/` -- API key, bearer token, basic auth, and HMAC authenticators
- `rate_limiting/` -- Fixed window, sliding window, token bucket, composite limiters, and middleware
- `circuit_breaker/` -- Circuit breaker, retry policy, and bulkhead patterns
- `webhooks/` -- Webhook dispatch, registry, signature verification, and transport
- `mocking/` -- Mock API server, request matching, and response fixtures
- `pagination/` -- Offset, cursor, and keyset pagination implementations
- `openapi_generator.py` -- Shared OpenAPI generator components used across submodules

## Quick Start

```python
from codomyrmex.api import create_api, create_router, create_rate_limiter, CircuitBreaker

# Build a REST API with a router
api = create_api(title="My Service", version="1.0.0")
router = create_router(prefix="/users")
api.add_router(router)

# Add rate limiting (100 requests per 60-second window)
limiter = create_rate_limiter(strategy="token_bucket", max_tokens=100, refill_rate=10)
result = limiter.check("client-ip-123")
print(f"Allowed: {result.allowed}, Remaining: {result.remaining}")

# Protect external calls with a circuit breaker
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
response = breaker.call(lambda: api.handle_request("/users", method="GET"))
```


## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`rate_limiting/`** | API rate limiting with token bucket and sliding window algorithms |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/api/](../../../docs/modules/api/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
