# api/standardization — Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The standardization submodule provides complete REST API and GraphQL API frameworks alongside API versioning. It enforces consistent routing, middleware composition, version management, and OpenAPI documentation.

## Architecture

```
standardization/
├── __init__.py          # Re-exports from all submodules and parent openapi_generator
├── rest_api.py          # RESTAPI, APIRouter, APIEndpoint, APIRequest, APIResponse, HTTPMethod, HTTPStatus
├── graphql_api.py       # GraphQLAPI, GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLResolver, GraphQLMutation, GraphQLQuery
├── api_versioning.py    # APIVersionManager, APIVersion, VersionedEndpoint, VersionFormat, decorators, factories
```

## Key Classes

### RESTAPI — `rest_api.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(title, version, description)` | Initialize with default logging and error-handling middleware |
| `handle_request` | `(method, path, headers, body, query_string) -> APIResponse` | Full request lifecycle: parse, middleware, route match, dispatch |
| `add_middleware` | `(middleware: Callable) -> None` | Add global middleware function |
| `add_router` | `(router: APIRouter) -> None` | Mount a sub-router |
| `get_metrics` | `() -> dict` | Request count, error count, error rate, endpoint count |
| `get_endpoints` | `() -> list[APIEndpoint]` | All registered endpoints including sub-routers |

### APIRouter — `rest_api.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_endpoint` | `(endpoint: APIEndpoint) -> None` | Register an endpoint |
| `get/post/put/delete/patch` | `(path, summary, **kwargs) -> decorator` | Decorator-based route registration |
| `match_endpoint` | `(method, path) -> tuple[APIEndpoint, dict] \| None` | Route matching with path parameter extraction |
| `add_router` | `(router: APIRouter) -> None` | Nest sub-routers |

### GraphQLAPI — `graphql_api.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(schema: GraphQLSchema)` | Initialize with schema; registers `__typename` resolver |
| `execute_query` | `(query, variables, context) -> dict` | Parse, validate complexity, execute, return `{"data":...}` or `{"errors":...}` |
| `register_resolver` | `(type_name, field_name, resolver) -> None` | Register a field resolver |
| `register_mutation` | `(mutation: GraphQLMutation) -> None` | Register a mutation |
| `validate_query` | `(query: str) -> list[str]` | Return validation errors |
| `get_schema_sdl` | `() -> str` | Generate Schema Definition Language output |
| `get_metrics` | `() -> dict` | Request/error counts, registered resolvers/mutations |

### GraphQLSchema — `graphql_api.py`

| Field | Type | Description |
|-------|------|-------------|
| `query_type` | `GraphQLObjectType \| None` | Root query type |
| `mutation_type` | `GraphQLObjectType \| None` | Root mutation type |
| `subscription_type` | `GraphQLObjectType \| None` | Root subscription type |
| `types` | `dict[str, GraphQLObjectType]` | Named type registry |
| `generate_sdl()` | `-> str` | Render full SDL string |

### APIVersionManager — `api_versioning.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(default_version, version_format)` | Initialize and register default version |
| `register_version` | `(version: APIVersion) -> None` | Add a version; validates format consistency |
| `parse_version_from_request` | `(headers, query_params) -> str` | Extract version from `X-API-Version`, `?version=`, or `Accept` header |
| `add_migration_rule` | `(from_version, to_version, migrator) -> None` | Register a data migration callable |
| `migrate_data` | `(data, from_version, to_version) -> Any` | Walk migration path to transform data |
| `get_version_info` | `() -> dict` | Summary of all versions with metadata |
| `check_deprecated_usage` | `(version, endpoint) -> bool` | Check if version/endpoint combination is deprecated |

### VersionFormat (Enum)

| Member | Value | Example |
|--------|-------|---------|
| `SEMVER` | `"semver"` | `1.0.0` |
| `DATE` | `"date"` | `2024-01-01` |
| `INTEGER` | `"int"` | `1`, `2`, `3` |

## Design Decisions

- **Regex-based route matching**: `APIRouter._path_to_regex` converts `{param}` patterns to named capture groups for flexible path parameter extraction.
- **Simplified GraphQL parser**: `_parse_query` is a basic implementation; production use should integrate a full GraphQL parser library.
- **Version migration chaining**: `migrate_data` walks a graph of migration rules, supporting multi-hop version transitions.

## Dependencies

- `re`, `json`, `time`, `logging`, `datetime`, `enum`, `dataclasses`, `abc`, `urllib.parse` (stdlib)
- `codomyrmex.logging_monitoring.core.logger_config` for structured logging

## Navigation

- **Parent**: [api/SPEC.md](../SPEC.md)
- **Sibling**: [AGENTS.md](AGENTS.md) | [README.md](README.md)
