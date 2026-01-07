# Codomyrmex Agents — src/codomyrmex/api/standardization

## Signposting
- **Parent**: [api](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
API standardization including REST API, GraphQL API, and API versioning. Provides tools for standardizing API interfaces, validation, and compliance checking across different API types.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `api_versioning.py` – API versioning management
- `graphql_api.py` – GraphQL API implementation
- `rest_api.py` – REST API implementation

## Key Classes and Functions

### RESTAPI (`rest_api.py`)
- `RESTAPI()` – REST API implementation
- `create_endpoint(path: str, method: str, handler: callable) -> None` – Create REST endpoint
- `validate_request(request: dict) -> bool` – Validate REST request

### GraphQLAPI (`graphql_api.py`)
- `GraphQLAPI()` – GraphQL API implementation
- `execute_query(query: str, variables: dict = None) -> dict` – Execute GraphQL query
- `validate_schema(schema: str) -> bool` – Validate GraphQL schema

### APIVersioner (`api_versioning.py`)
- `APIVersioner()` – API versioning management
- `version_api(api: dict, version: str) -> dict` – Version API
- `get_version(api: dict) -> str` – Get API version

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [api](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation