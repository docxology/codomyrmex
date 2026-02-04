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
"""

# Import from documentation submodule
from .documentation import (
    # Documentation generation
    APIDocumentationGenerator,
    generate_api_docs,
    extract_api_specs,
    APIDocumentation,
    APIEndpoint as DocumentationAPIEndpoint,
    # OpenAPI/Swagger
    OpenAPIGenerator as DocumentationOpenAPIGenerator,
    generate_openapi_spec as generate_openapi_spec_from_docs,
    validate_openapi_spec,
    APISchema,
)

# Import from standardization submodule
from .standardization import (
    # REST API
    RESTAPI,
    APIEndpoint as StandardizationAPIEndpoint,
    APIResponse,
    APIRouter,
    HTTPMethod,
    HTTPStatus,
    APIRequest,
    create_api,
    create_router,
    # GraphQL API
    GraphQLAPI,
    GraphQLSchema,
    GraphQLResolver,
    GraphQLMutation,
    GraphQLObjectType,
    GraphQLField,
    GraphQLQuery,
    GraphQLType,
    resolver,
    mutation,
    create_schema,
    create_object_type,
    create_field,
    # API Versioning
    APIVersionManager,
    APIVersion,
    VersionedEndpoint,
    VersionFormat,
    version,
    deprecated_version,
    create_version_manager,
    create_versioned_endpoint,
    # OpenAPI Generation
    OpenAPIGenerator as StandardizationOpenAPIGenerator,
    OpenAPISpecification,
    generate_openapi_spec as generate_openapi_spec_from_api,
    create_openapi_from_rest_api,
    create_openapi_from_graphql_api,
)

# Import shared OpenAPI components
from .openapi_generator import (
    DocumentationOpenAPIGenerator,
    StandardizationOpenAPIGenerator,
    OpenAPISpecification,
    APISchema as SharedAPISchema,
)

# Import from authentication submodule
from .authentication import (
    AuthType,
    AuthCredentials,
    AuthResult,
    Authenticator,
    APIKeyAuthenticator,
    BearerTokenAuthenticator,
    BasicAuthenticator,
    HMACAuthenticator,
    create_authenticator,
)

# Import from rate_limiting submodule
from .rate_limiting import (
    RateLimitStrategy,
    RateLimitResult,
    RateLimiter as RateLimiterBase,
    FixedWindowLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    CompositeRateLimiter,
    RateLimiterMiddleware,
    create_rate_limiter,
)

# Import from circuit_breaker submodule
from .circuit_breaker import (
    CircuitState,
    CircuitStats,
    CircuitBreakerConfig,
    CircuitBreaker,
    RetryPolicy,
    Bulkhead,
    CircuitOpenError,
    BulkheadFullError,
    circuit_breaker as circuit_breaker_decorator,
    retry,
)

# Import from webhooks submodule
from .webhooks import (
    WebhookEventType,
    WebhookStatus,
    SignatureAlgorithm,
    WebhookEvent,
    WebhookConfig,
    DeliveryResult,
    WebhookTransport,
    HTTPWebhookTransport,
    WebhookSignature,
    WebhookRegistry,
    WebhookDispatcher,
    create_webhook_registry,
    create_webhook_dispatcher,
)

# Import from mocking submodule
from .mocking import (
    MatchStrategy,
    MockResponseMode,
    MockRequest,
    MockResponse,
    MockRoute,
    RequestLog,
    RequestMatcher,
    MockAPIServer,
    ResponseFixture,
    create_mock_server,
    create_fixture,
)

# Import from pagination submodule
from .pagination import (
    PaginationStrategy,
    SortDirection,
    PageInfo,
    PaginatedResponse,
    PaginationRequest,
    Paginator,
    OffsetPaginator,
    CursorPaginator,
    KeysetPaginator,
    create_paginator,
)

__all__ = [
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
]
