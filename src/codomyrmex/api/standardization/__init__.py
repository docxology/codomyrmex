"""
API Standardization Module for Codomyrmex

This module provides standardized API interfaces including REST API, GraphQL API,
API versioning, and OpenAPI specification generation for consistent API development.
"""

# REST API components
from codomyrmex.api.openapi_generator import (
    OpenAPISpecification,
    create_openapi_from_graphql_api,
    create_openapi_from_rest_api,
)

# OpenAPI Generation components (from parent module)
from codomyrmex.api.openapi_generator import (
    StandardizationOpenAPIGenerator as OpenAPIGenerator,
)
from codomyrmex.api.openapi_generator import (
    create_openapi_generator as generate_openapi_spec,
)

# API Versioning components
from .api_versioning import (
    APIVersion,
    APIVersionManager,
    VersionedEndpoint,
    VersionFormat,
    create_version_manager,
    create_versioned_endpoint,
    deprecated_version,
    version,
)

# GraphQL API components
from .graphql_api import (
    GraphQLAPI,
    GraphQLField,
    GraphQLMutation,
    GraphQLObjectType,
    GraphQLQuery,
    GraphQLResolver,
    GraphQLSchema,
    GraphQLType,
    create_field,
    create_object_type,
    create_schema,
    mutation,
    resolver,
)
from .rest_api import (
    RESTAPI,
    APIEndpoint,
    APIRequest,
    APIResponse,
    APIRouter,
    HTTPMethod,
    HTTPStatus,
    create_api,
    create_router,
)

__all__ = [
    # REST API
    "RESTAPI",
    "APIEndpoint",
    "APIRequest",
    "APIResponse",
    "APIRouter",
    "APIVersion",
    # API Versioning
    "APIVersionManager",
    # GraphQL API
    "GraphQLAPI",
    "GraphQLField",
    "GraphQLMutation",
    "GraphQLObjectType",
    "GraphQLQuery",
    "GraphQLResolver",
    "GraphQLSchema",
    "GraphQLType",
    "HTTPMethod",
    "HTTPStatus",
    # OpenAPI Generation
    "OpenAPIGenerator",
    "OpenAPISpecification",
    "VersionFormat",
    "VersionedEndpoint",
    "create_api",
    "create_field",
    "create_object_type",
    "create_openapi_from_graphql_api",
    "create_openapi_from_rest_api",
    "create_router",
    "create_schema",
    "create_version_manager",
    "create_versioned_endpoint",
    "deprecated_version",
    "generate_openapi_spec",
    "mutation",
    "resolver",
    "version",
]
