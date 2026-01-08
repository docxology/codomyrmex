"""
Unified API Module for Codomyrmex.

This module provides comprehensive API functionality including:
- API documentation generation and management
- API standardization (REST, GraphQL, versioning)
- OpenAPI specification generation

The module is organized into submodules:
- documentation: API documentation generation from code analysis
- standardization: REST/GraphQL API frameworks and versioning
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
]


