# API Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The API module provides comprehensive API infrastructure for Codomyrmex, including documentation generation, REST/GraphQL standardization, versioning, and OpenAPI specification support.

## Submodules

| Submodule | Purpose |
|-----------|---------|
| `documentation/` | API documentation generation from code analysis |
| `standardization/` | REST/GraphQL API frameworks and versioning |

## Key Features

- **REST API Builder**: Create RESTful APIs with routers and endpoints
- **GraphQL Support**: Schema, resolvers, mutations, and queries
- **API Versioning**: Version management with deprecation support
- **OpenAPI Generation**: Generate OpenAPI specs from REST or GraphQL APIs
- **Documentation Generation**: Extract and generate API docs from code

## Quick Start

```python
from codomyrmex.api import (
    RESTAPI, create_router, HTTPMethod,
    GraphQLAPI, create_schema,
    APIVersionManager, create_version_manager,
    generate_openapi_spec_from_api,
)

# Create a REST API
api = RESTAPI(name="MyAPI", base_path="/api")
router = create_router("/users")
router.add_endpoint("/", HTTPMethod.GET, handler=list_users)
api.add_router(router)

# Create versioned API
version_manager = create_version_manager("v1.0.0")
version_manager.add_version("v2.0.0", deprecated=False)

# Generate OpenAPI specification
spec = generate_openapi_spec_from_api(api)
```

## Core Classes

### REST API
| Class | Description |
|-------|-------------|
| `RESTAPI` | Main REST API class |
| `APIRouter` | Route grouping and organization |
| `APIEndpoint` | Individual API endpoint |
| `APIRequest` / `APIResponse` | Request/response models |
| `HTTPMethod` / `HTTPStatus` | HTTP enums |

### GraphQL
| Class | Description |
|-------|-------------|
| `GraphQLAPI` | Main GraphQL API class |
| `GraphQLSchema` | Schema definition |
| `GraphQLResolver` | Query resolvers |
| `GraphQLMutation` | Mutations |
| `GraphQLObjectType` / `GraphQLField` | Type system |

### Versioning
| Class | Description |
|-------|-------------|
| `APIVersionManager` | Version management |
| `APIVersion` | Version definition |
| `VersionedEndpoint` | Version-specific endpoints |

### Documentation
| Class | Description |
|-------|-------------|
| `APIDocumentationGenerator` | Generate docs from code |
| `OpenAPIGenerator` | OpenAPI spec generation |
| `OpenAPISpecification` | Spec model |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
