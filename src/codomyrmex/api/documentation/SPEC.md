# api/documentation — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The documentation submodule generates API reference material from Python source code. It uses AST introspection to discover endpoints and produces OpenAPI 3.0.3-compliant specifications.

## Architecture

```
documentation/
├── __init__.py       # Re-exports from doc_generator and parent openapi_generator
├── doc_generator.py  # APIDocumentationGenerator, APIEndpoint, APIDocumentation
```

## Key Classes

### APIEndpoint (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | URL path pattern (e.g., `/users/{id}`) |
| `method` | `str` | HTTP method (GET, POST, etc.) |
| `summary` | `str \| None` | Short description from docstring |
| `description` | `str \| None` | Full description |
| `parameters` | `list[dict]` | Path/query parameter definitions |
| `request_body` | `dict \| None` | Request body schema |
| `responses` | `dict[int, dict]` | Status code to response schema mapping |
| `tags` | `list[str]` | Grouping tags |

### APIDocumentation (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | API title |
| `version` | `str` | API version string |
| `description` | `str` | API description |
| `endpoints` | `list[APIEndpoint]` | All discovered endpoints |
| `tags` | `list[dict]` | Tag definitions |

### APIDocumentationGenerator

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(source_dir: str)` | Set source directory for scanning |
| `discover_endpoints` | `() -> list[APIEndpoint]` | AST-walk Python files to find route handlers |
| `generate_openapi_spec` | `() -> dict` | Build OpenAPI 3.0.3 spec dict from discovered endpoints |
| `export_json` | `(path: str) -> None` | Write spec as JSON file |
| `export_yaml` | `(path: str) -> None` | Write spec as YAML file |
| `validate_spec` | `() -> list[str]` | Return list of validation warnings |

## Design Decisions

- **AST parsing over runtime introspection**: Avoids importing modules with side effects; works on any Python file regardless of import availability.
- **OpenAPI 3.0.3**: Chosen for broad tooling compatibility (Swagger UI, Redoc, code generators).

## Dependencies

- `ast`, `json` (stdlib)
- Parent module `openapi_generator.py` for `OpenAPISpecification` and `StandardizationOpenAPIGenerator`

## Navigation

- **Parent**: [api/SPEC.md](../SPEC.md)
- **Sibling**: [AGENTS.md](AGENTS.md) | [README.md](README.md)
