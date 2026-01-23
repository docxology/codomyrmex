# Codomyrmex Agents — src/codomyrmex/api/standardization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides standardized API interfaces including REST API, GraphQL API, API versioning, and OpenAPI specification generation for consistent API development across the Codomyrmex ecosystem.

## Active Components

- `rest_api.py` - REST API framework and utilities
- `graphql_api.py` - GraphQL schema and resolver framework
- `api_versioning.py` - API version management
- `__init__.py` - Module exports
- `API_SPECIFICATION.md` - API documentation
- `CHANGELOG.md` - Version history

## Key Classes and Functions

### rest_api.py
- **`RESTAPI`** - Main REST API application
- **`APIRouter`** - Route grouping and organization
- **`APIEndpoint`** - Individual endpoint definition
- **`APIRequest`** - Request wrapper with validation
- **`APIResponse`** - Standardized response format
- **`HTTPMethod`** - Enum: GET, POST, PUT, DELETE, PATCH
- **`HTTPStatus`** - HTTP status code enum
- **`create_api()`**, **`create_router()`** - Factory functions

### graphql_api.py
- **`GraphQLAPI`** - GraphQL API application
- **`GraphQLSchema`** - Schema definition
- **`GraphQLResolver`** - Query resolver decorator
- **`GraphQLMutation`** - Mutation resolver decorator
- **`GraphQLObjectType`**, **`GraphQLField`** - Type definitions
- **`GraphQLQuery`**, **`GraphQLType`** - Query building
- **`@resolver`**, **`@mutation`** - Decorators
- **`create_schema()`**, **`create_object_type()`**, **`create_field()`** - Factory functions

### api_versioning.py
- **`APIVersionManager`** - Manages API versions
- **`APIVersion`** - Version definition (major.minor.patch)
- **`VersionedEndpoint`** - Endpoint with version constraints
- **`VersionFormat`** - Versioning schemes (URL, header, query)
- **`@version`**, **`@deprecated_version`** - Decorators
- **`create_version_manager()`**, **`create_versioned_endpoint()`** - Factory functions

### OpenAPI Integration (from parent module)
- **`OpenAPIGenerator`** - Generates OpenAPI/Swagger specs
- **`OpenAPISpecification`** - Spec data structure
- **`generate_openapi_spec()`** - Generate from API definition
- **`create_openapi_from_rest_api()`**, **`create_openapi_from_graphql_api()`** - Converters

## Operating Contracts

- REST endpoints follow RESTful conventions
- GraphQL schema validates queries before execution
- Version negotiation respects Accept headers
- OpenAPI specs are OpenAPI 3.0 compliant
- All responses include standard metadata (timestamp, version)

## Signposting

- **Dependencies**: May use frameworks like FastAPI, Starlette
- **Parent Directory**: [api](../README.md) - Parent module documentation
- **Related Modules**:
  - `../openapi_generator.py` - OpenAPI spec generation
  - `model_context_protocol/` - MCP API definitions
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
