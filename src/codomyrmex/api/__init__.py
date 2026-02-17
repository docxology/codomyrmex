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

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

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
    # OpenAPI/Swagger
    OpenAPIGenerator as DocumentationOpenAPIGenerator,
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
    OpenAPISpecification,
    StandardizationOpenAPIGenerator,
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
    RateLimiterMiddleware,
    RateLimitResult,
    RateLimitStrategy,
    SlidingWindowLimiter,
    TokenBucketLimiter,
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


from . import rate_limiting

__all__ = [
    "rate_limiting",
    # Documentation submodule exports
    "APIDocumentationGenerator",
    "generate_api_docs",
    "extract_api_specs",
    "APIDocumentation",
    "DocumentationAPIEndpoint",
    "DocumentationOpenAPIGenerator",
    "generate_openapi_spec_from_docs",
    "validate_openapi_spec",
    "APISchema",
    # Standardization submodule exports
    "RESTAPI",
    "StandardizationAPIEndpoint",
    "APIResponse",
    "APIRouter",
    "HTTPMethod",
    "HTTPStatus",
    "APIRequest",
    "create_api",
    "create_router",
    "GraphQLAPI",
    "GraphQLSchema",
    "GraphQLResolver",
    "GraphQLMutation",
    "GraphQLObjectType",
    "GraphQLField",
    "GraphQLQuery",
    "GraphQLType",
    "resolver",
    "mutation",
    "create_schema",
    "create_object_type",
    "create_field",
    "APIVersionManager",
    "APIVersion",
    "VersionedEndpoint",
    "VersionFormat",
    "version",
    "deprecated_version",
    "create_version_manager",
    "create_versioned_endpoint",
    "StandardizationOpenAPIGenerator",
    "OpenAPISpecification",
    "generate_openapi_spec_from_api",
    "create_openapi_from_rest_api",
    "create_openapi_from_graphql_api",
    # Shared components
    "SharedAPISchema",
    # Authentication
    "AuthType",
    "AuthCredentials",
    "AuthResult",
    "Authenticator",
    "APIKeyAuthenticator",
    "BearerTokenAuthenticator",
    "BasicAuthenticator",
    "HMACAuthenticator",
    "create_authenticator",
    # Rate limiting
    "RateLimitStrategy",
    "RateLimitResult",
    "RateLimiterBase",
    "FixedWindowLimiter",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    "CompositeRateLimiter",
    "RateLimiterMiddleware",
    "create_rate_limiter",
    # Circuit breaker
    "CircuitState",
    "CircuitStats",
    "CircuitBreakerConfig",
    "CircuitBreaker",
    "RetryPolicy",
    "Bulkhead",
    "CircuitOpenError",
    "BulkheadFullError",
    "circuit_breaker_decorator",
    "retry",
    # Webhooks
    "WebhookEventType",
    "WebhookStatus",
    "SignatureAlgorithm",
    "WebhookEvent",
    "WebhookConfig",
    "DeliveryResult",
    "WebhookTransport",
    "HTTPWebhookTransport",
    "WebhookSignature",
    "WebhookRegistry",
    "WebhookDispatcher",
    "create_webhook_registry",
    "create_webhook_dispatcher",
    # Mocking
    "MatchStrategy",
    "MockResponseMode",
    "MockRequest",
    "MockResponse",
    "MockRoute",
    "RequestLog",
    "RequestMatcher",
    "MockAPIServer",
    "ResponseFixture",
    "create_mock_server",
    "create_fixture",
    # Pagination
    "PaginationStrategy",
    "SortDirection",
    "PageInfo",
    "PaginatedResponse",
    "PaginationRequest",
    "Paginator",
    "OffsetPaginator",
    "CursorPaginator",
    "KeysetPaginator",
    "create_paginator",
    "cli_commands",
]
