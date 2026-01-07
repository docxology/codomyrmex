# standardization

## Signposting
- **Parent**: [standardization](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

API standardization including REST API, GraphQL API, and API versioning. Provides tools for standardizing API interfaces, validation, and compliance checking across different API types.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `api_versioning.py` – File
- `graphql_api.py` – File
- `rest_api.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [api](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.api.standardization import (
    RESTAPI,
    create_api,
    APIVersionManager,
    GraphQLAPI,
    create_schema,
)

# Create a REST API
api = create_api("v1")
router = api.create_router()

@router.get("/users")
def get_users():
    return {"users": []}

# API versioning
version_manager = APIVersionManager()
version_manager.register_version("v1", api)

# Create GraphQL schema
schema = create_schema()
query = schema.create_query()
query.field("users", lambda: [])
```

