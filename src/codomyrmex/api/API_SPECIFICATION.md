# API Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `api` module provides foundations for defining, documenting, and standardizing APIs within Codomyrmex. It supports REST and GraphQL paradigms and includes automated documentation generation.

## 2. Core Components

### 2.1 Documentation
- **`APIDocumentationGenerator`**: Analyzes code to produce API docs.
- **`generate_api_docs`**: Helper function to trigger doc generation.
- **`generate_openapi_spec_from_docs`**: Converts internal docs to OpenAPI 3.0.

### 2.2 Standardization
- **`RESTAPI`**: Framework for defining RESTful interfaces.
- **`GraphQLAPI`**: Framework for defining GraphQL schemas.
- **`APIVersionManager`**: Handles API versioning strategies.

### 2.3 Data Structures
- **`APIEndpoint`**: Metadata for a single API route.
- **`APISchema`**: Definition of data models.
- **`OpenAPISpecification`**: Wrapper for OpenAPI structure.

## 3. Usage Example

```python
from codomyrmex.api import RESTAPI, create_router

app = RESTAPI(title="My Service")
router = create_router()

@router.get("/items")
def get_items():
    return [{"id": 1}]

app.include_router(router)
```
