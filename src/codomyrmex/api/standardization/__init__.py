"""
API Standardization Module for Codomyrmex

This module provides standardized API interfaces including REST API, GraphQL API,
API versioning, and OpenAPI specification generation for consistent API development.
"""

# REST API components
from ..openapi_generator import (
    OpenAPISpecification,
    create_openapi_from_graphql_api,
    create_openapi_from_rest_api,
)

# OpenAPI Generation components (from parent module)
from ..openapi_generator import StandardizationOpenAPIGenerator as OpenAPIGenerator
from ..openapi_generator import create_openapi_generator as generate_openapi_spec

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
    'RESTAPI', 'APIEndpoint', 'APIResponse', 'APIRouter', 'HTTPMethod', 'HTTPStatus',
    'APIRequest', 'create_api', 'create_router',

    # GraphQL API
    'GraphQLAPI', 'GraphQLSchema', 'GraphQLResolver', 'GraphQLMutation',
    'GraphQLObjectType', 'GraphQLField', 'GraphQLQuery', 'GraphQLType',
    'resolver', 'mutation', 'create_schema', 'create_object_type', 'create_field',

    # API Versioning
    'APIVersionManager', 'APIVersion', 'VersionedEndpoint', 'VersionFormat',
    'version', 'deprecated_version', 'create_version_manager', 'create_versioned_endpoint',

    # OpenAPI Generation
    'OpenAPIGenerator', 'OpenAPISpecification',
    'generate_openapi_spec', 'create_openapi_from_rest_api', 'create_openapi_from_graphql_api'
]
