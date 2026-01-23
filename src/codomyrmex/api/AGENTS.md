# Codomyrmex Agents — src/codomyrmex/api

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The API module provides a unified framework for API development, documentation generation, and standardization within the Codomyrmex ecosystem. It supports REST API development with automatic routing and middleware, GraphQL API with schema generation and resolvers, API versioning with backward compatibility management, and OpenAPI specification generation from both code analysis and API instances.

## Active Components

### Documentation Submodule (`documentation/`)

- `doc_generator.py` - API documentation generation from code analysis
  - Key Classes: `APIDocumentationGenerator`, `APIDocumentation`, `APIEndpoint`
  - Key Functions: `generate_api_docs()`, `extract_api_specs()`

### Standardization Submodule (`standardization/`)

- `rest_api.py` - REST API framework with routing and middleware
  - Key Classes: `RESTAPI`, `APIRouter`, `APIEndpoint`, `APIRequest`, `APIResponse`
  - Key Functions: `create_api()`, `create_router()`
  - Key Enums: `HTTPMethod`, `HTTPStatus`

- `graphql_api.py` - GraphQL API framework with schema generation
  - Key Classes: `GraphQLAPI`, `GraphQLSchema`, `GraphQLObjectType`, `GraphQLField`, `GraphQLResolver`, `GraphQLMutation`, `GraphQLQuery`
  - Key Functions: `create_schema()`, `create_object_type()`, `create_field()`
  - Decorators: `@resolver`, `@mutation`

- `api_versioning.py` - API version management and migration
  - Key Classes: `APIVersionManager`, `APIVersion`, `VersionedEndpoint`
  - Key Functions: `create_version_manager()`, `create_versioned_endpoint()`
  - Decorators: `@version`, `@deprecated_version`
  - Key Enums: `VersionFormat`

### Root Level

- `openapi_generator.py` - Unified OpenAPI specification generation
  - Key Classes: `DocumentationOpenAPIGenerator`, `StandardizationOpenAPIGenerator`, `OpenAPISpecification`, `APISchema`
  - Key Functions: `generate_openapi_spec()`, `validate_openapi_spec()`, `create_openapi_from_rest_api()`, `create_openapi_from_graphql_api()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `RESTAPI` | standardization.rest_api | Main REST API class handling HTTP requests and responses |
| `APIRouter` | standardization.rest_api | Router for managing API endpoints with method decorators |
| `GraphQLAPI` | standardization.graphql_api | Main GraphQL API class for handling GraphQL requests |
| `GraphQLSchema` | standardization.graphql_api | GraphQL schema definition with SDL generation |
| `APIVersionManager` | standardization.api_versioning | Manages API versions, endpoints, and migration rules |
| `APIDocumentationGenerator` | documentation.doc_generator | Automatic API discovery and documentation generation |
| `DocumentationOpenAPIGenerator` | openapi_generator | OpenAPI spec generation from endpoint lists |
| `StandardizationOpenAPIGenerator` | openapi_generator | OpenAPI spec generation from REST/GraphQL API instances |
| `create_api()` | standardization.rest_api | Factory function for REST API instances |
| `generate_api_docs()` | documentation.doc_generator | Generate API documentation from source paths |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging
2. **API Discovery**: Documentation generator scans source code via AST analysis to discover API endpoints
3. **Version Compatibility**: APIVersionManager supports semver, date, and integer version formats
4. **Middleware Support**: REST API supports global middleware, router middleware, and endpoint-specific middleware
5. **GraphQL Complexity**: GraphQL API includes query complexity limiting to prevent expensive queries
6. **OpenAPI Compliance**: All generators produce OpenAPI 3.0.3 compliant specifications
7. **Error Handling**: REST API provides standardized error responses via `APIResponse.error()`, `APIResponse.not_found()`, `APIResponse.bad_request()`

## Integration Points

- **logging_monitoring** - All API components log via centralized logger
- **static_analysis** - Documentation module uses code introspection for API discovery
- **security** - API security documentation and authentication schemes
- **data_visualization** - API usage analytics (planned)

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Centralized logging |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security and authentication |
| static_analysis | [../static_analysis/AGENTS.md](../static_analysis/AGENTS.md) | Code analysis |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| documentation/ | API documentation generation from code analysis |
| standardization/ | REST, GraphQL, and versioning frameworks |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
