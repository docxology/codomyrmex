"""
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


Submodules:
    rate_limiting: Consolidated rate limiting capabilities."""

from . import rate_limiting

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    pass

# Import from documentation submodule
# Import from authentication submodule
from .authentication import (
    APIKeyAuthenticator,
    AuthCredentials,
    Authenticator,
    AuthResult,
    AuthType,
    BasicAuthenticator,
    BearerTokenAuthenticator,
    HMACAuthenticator,
    create_authenticator,
)

# Import from circuit_breaker submodule
from .circuit_breaker import (
    Bulkhead,
    BulkheadFullError,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    CircuitStats,
    RetryPolicy,
    retry,
)
from .circuit_breaker import (
    circuit_breaker as circuit_breaker_decorator,
)
from .documentation import (
    APIDocumentation,
    # Documentation generation
    APIDocumentationGenerator,
    APISchema,
    extract_api_specs,
    generate_api_docs,
    validate_openapi_spec,
)
from .documentation import (
    APIEndpoint as DocumentationAPIEndpoint,
)
from .documentation import (
    generate_openapi_spec as generate_openapi_spec_from_docs,
)

# Import from mocking submodule
from .mocking import (
    MatchStrategy,
    MockAPIServer,
    MockRequest,
    MockResponse,
    MockResponseMode,
    MockRoute,
    RequestLog,
    RequestMatcher,
    ResponseFixture,
    create_fixture,
    create_mock_server,
)
from .openapi_generator import (
    APISchema as SharedAPISchema,
)

# Import shared OpenAPI components
from .openapi_generator import (
    DocumentationOpenAPIGenerator,
)

# Import from pagination submodule
from .pagination import (
    CursorPaginator,
    KeysetPaginator,
    OffsetPaginator,
    PageInfo,
    PaginatedResponse,
    PaginationRequest,
    PaginationStrategy,
    Paginator,
    SortDirection,
    create_paginator,
)

# Import from rate_limiting submodule
from .rate_limiting import (
    CompositeRateLimiter,
    FixedWindowLimiter,
    QuotaManager,
    RateLimiterMiddleware,
    RateLimitExceeded,
    RateLimitResult,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    create_limiter,
    create_rate_limiter,
)
from .rate_limiting import (
    RateLimiter as RateLimiterBase,
)

# Import from standardization submodule
from .standardization import (
    # REST API
    RESTAPI,
    APIRequest,
    APIResponse,
    APIRouter,
    APIVersion,
    # API Versioning
    APIVersionManager,
    # GraphQL API
    GraphQLAPI,
    GraphQLField,
    GraphQLMutation,
    GraphQLObjectType,
    GraphQLQuery,
    GraphQLResolver,
    GraphQLSchema,
    GraphQLType,
    HTTPMethod,
    HTTPStatus,
    OpenAPISpecification,
    VersionedEndpoint,
    VersionFormat,
    create_api,
    create_field,
    create_object_type,
    create_openapi_from_graphql_api,
    create_openapi_from_rest_api,
    create_router,
    create_schema,
    create_version_manager,
    create_versioned_endpoint,
    deprecated_version,
    mutation,
    resolver,
    version,
)
from .standardization import (
    APIEndpoint as StandardizationAPIEndpoint,
)
from .standardization import (
    # OpenAPI Generation
    OpenAPIGenerator as StandardizationOpenAPIGenerator,
)
from .standardization import (
    generate_openapi_spec as generate_openapi_spec_from_api,
)

# Import from webhooks submodule
from .webhooks import (
    DeliveryResult,
    HTTPWebhookTransport,
    SignatureAlgorithm,
    WebhookConfig,
    WebhookDispatcher,
    WebhookEvent,
    WebhookEventType,
    WebhookRegistry,
    WebhookSignature,
    WebhookStatus,
    WebhookTransport,
    create_webhook_dispatcher,
    create_webhook_registry,
)


def cli_commands():
    """Return CLI commands for the API module."""

    def _list_routes():
        """List API routes."""
        print("API Module - Route Types:")
        print("  REST API routes (via RESTAPI / APIRouter)")
        print("  GraphQL endpoints (via GraphQLAPI / GraphQLSchema)")
        print("  Webhook endpoints (via WebhookRegistry)")
        print("  Mock routes (via MockAPIServer)")

    def _api_status():
        """Show API status."""
        print("API Module Status:")
        print("  Authentication: APIKey, Bearer, Basic, HMAC")
        print("  Rate Limiting: FixedWindow, SlidingWindow, TokenBucket")
        print("  Resilience: CircuitBreaker, RetryPolicy, Bulkhead")
        print("  Pagination: Offset, Cursor, Keyset")
        print("  Webhooks: available")
        print("  Mocking: available")

    return {
        "routes": _list_routes,
        "status": _api_status,
    }


__all__ = [
    # Standardization submodule exports
    "RESTAPI",
    "APIDocumentation",
    # Documentation submodule exports
    "APIDocumentationGenerator",
    "APIKeyAuthenticator",
    "APIRequest",
    "APIResponse",
    "APIRouter",
    "APISchema",
    "APIVersion",
    "APIVersionManager",
    "AuthCredentials",
    "AuthResult",
    # Authentication
    "AuthType",
    "Authenticator",
    "BasicAuthenticator",
    "BearerTokenAuthenticator",
    "Bulkhead",
    "BulkheadFullError",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    # Circuit breaker
    "CircuitState",
    "CircuitStats",
    "CompositeRateLimiter",
    "CursorPaginator",
    "DeliveryResult",
    "DocumentationAPIEndpoint",
    "DocumentationOpenAPIGenerator",
    "FixedWindowLimiter",
    "GraphQLAPI",
    "GraphQLField",
    "GraphQLMutation",
    "GraphQLObjectType",
    "GraphQLQuery",
    "GraphQLResolver",
    "GraphQLSchema",
    "GraphQLType",
    "HMACAuthenticator",
    "HTTPMethod",
    "HTTPStatus",
    "HTTPWebhookTransport",
    "KeysetPaginator",
    # Mocking
    "MatchStrategy",
    "MockAPIServer",
    "MockRequest",
    "MockResponse",
    "MockResponseMode",
    "MockRoute",
    "OffsetPaginator",
    "OpenAPISpecification",
    "PageInfo",
    "PaginatedResponse",
    "PaginationRequest",
    # Pagination
    "PaginationStrategy",
    "Paginator",
    "QuotaManager",
    # Rate limiting
    "RateLimitExceeded",
    "RateLimitResult",
    "RateLimiterBase",
    "RateLimiterMiddleware",
    "RequestLog",
    "RequestMatcher",
    "ResponseFixture",
    "RetryPolicy",
    # Shared components
    "SharedAPISchema",
    "SignatureAlgorithm",
    "SlidingWindowLimiter",
    "SortDirection",
    "StandardizationAPIEndpoint",
    "StandardizationOpenAPIGenerator",
    "TokenBucketLimiter",
    "VersionFormat",
    "VersionedEndpoint",
    "WebhookConfig",
    "WebhookDispatcher",
    "WebhookEvent",
    # Webhooks
    "WebhookEventType",
    "WebhookRegistry",
    "WebhookSignature",
    "WebhookStatus",
    "WebhookTransport",
    "circuit_breaker_decorator",
    "cli_commands",
    "create_api",
    "create_authenticator",
    "create_field",
    "create_fixture",
    "create_limiter",
    "create_mock_server",
    "create_object_type",
    "create_openapi_from_graphql_api",
    "create_openapi_from_rest_api",
    "create_paginator",
    "create_rate_limiter",
    "create_router",
    "create_schema",
    "create_version_manager",
    "create_versioned_endpoint",
    "create_webhook_dispatcher",
    "create_webhook_registry",
    "deprecated_version",
    "extract_api_specs",
    "generate_api_docs",
    "generate_openapi_spec_from_api",
    "generate_openapi_spec_from_docs",
    "mutation",
    "rate_limiting",
    "resolver",
    "retry",
    "validate_openapi_spec",
    "version",
]
