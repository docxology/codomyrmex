# api

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [documentation](documentation/README.md)
    - [standardization](standardization/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

API infrastructure including OpenAPI specification generation, API documentation, and API standardization. Provides tools for generating OpenAPI specifications from code, standardizing API interfaces, and maintaining API documentation.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `documentation/` – Subdirectory
- `openapi_generator.py` – File
- `standardization/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.api import (
    RESTAPI,
    GraphQLAPI,
    OpenAPIGenerator,
    APIVersionManager,
)

# Create REST API
api = RESTAPI()
api.add_endpoint("/users", method="GET", handler=get_users)
api.add_endpoint("/users", method="POST", handler=create_user)

# Create GraphQL API
graphql = GraphQLAPI()
graphql.add_query("users", resolver=get_users)
graphql.add_mutation("createUser", resolver=create_user)

# Generate OpenAPI spec
openapi_gen = OpenAPIGenerator()
spec = openapi_gen.generate_from_routes(api.routes)
openapi_gen.save_spec(spec, "openapi.json")

# Version API
version_mgr = APIVersionManager()
versioned_api = version_mgr.create_versioned_endpoint(
    endpoint="/users",
    version="v1"
)
```

