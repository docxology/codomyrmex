"""
API Standardization Module for Codomyrmex

This module provides standardized API interfaces including REST API, GraphQL API,
API versioning, and OpenAPI specification generation for consistent API development.
"""

# REST API components
from .rest_api import (
    RESTAPI, APIEndpoint, APIResponse, APIRouter, HTTPMethod, HTTPStatus,
    APIRequest, create_api, create_router
)

# GraphQL API components
from .graphql_api import (
    GraphQLAPI, GraphQLSchema, GraphQLResolver, GraphQLMutation,
    GraphQLObjectType, GraphQLField, GraphQLQuery, GraphQLType,
    resolver, mutation, create_schema, create_object_type, create_field
)

# API Versioning components
from .api_versioning import (
    APIVersionManager, APIVersion, VersionedEndpoint, VersionFormat,
    version, deprecated_version, create_version_manager, create_versioned_endpoint
)

# OpenAPI Generation components
from .openapi_generator import (
    OpenAPIGenerator, OpenAPISpecification,
    generate_openapi_spec, create_openapi_from_rest_api, create_openapi_from_graphql_api
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
