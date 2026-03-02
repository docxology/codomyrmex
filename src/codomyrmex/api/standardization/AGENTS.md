# AI Agent Guidelines — api/standardization

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides standardized REST API and GraphQL API frameworks alongside API versioning with semantic version support, migration rules, and OpenAPI spec generation.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `RESTAPI` | `rest_api.py` | Main REST API: router, middleware pipeline, request handling, metrics |
| `APIRouter` | `rest_api.py` | Route registration with prefix support, parameterized path matching, sub-routers |
| `APIRequest` / `APIResponse` | `rest_api.py` | Request/response dataclasses with JSON body parsing and factory methods (`success`, `error`, `not_found`) |
| `APIEndpoint` | `rest_api.py` | Endpoint config: path, method, handler callable, middleware, OpenAPI metadata |
| `HTTPMethod` / `HTTPStatus` | `rest_api.py` | Enums for HTTP methods (7 values) and status codes (13 values) |
| `GraphQLAPI` | `graphql_api.py` | GraphQL request execution: query parsing, complexity limiting, resolver dispatch |
| `GraphQLSchema` | `graphql_api.py` | Schema container with SDL generation (`generate_sdl`) |
| `GraphQLObjectType` / `GraphQLField` | `graphql_api.py` | Type system building blocks |
| `GraphQLResolver` / `GraphQLMutation` | `graphql_api.py` | Field resolution and mutation execution with error logging |
| `APIVersionManager` | `api_versioning.py` | Version registry, request version parsing (headers/query/Accept), migration path resolution |
| `APIVersion` | `api_versioning.py` | Version metadata: format (semver/date/integer), deprecation, breaking changes |
| `VersionedEndpoint` | `api_versioning.py` | Maps version strings to handler callables with deprecation tracking |
| `version` / `deprecated_version` | `api_versioning.py` | Decorators for annotating handler functions with version metadata |

## Operating Contracts

- `RESTAPI.handle_request(method, path, headers, body, query_string)` is the main entry point for REST dispatch.
- `APIRouter` supports decorator-based registration (`@router.get("/path")`) and parametric route matching via regex.
- `GraphQLAPI.execute_query(query, variables, context)` returns `{"data": ...}` or `{"errors": [...]}`.
- `APIVersionManager.parse_version_from_request(headers, query_params)` extracts version from `X-API-Version` header, `?version=` query param, or `Accept` header with vendored content type.
- `migrate_data(data, from_version, to_version)` walks registered migration rules to transform data between versions.

## Integration Points

- **Parent**: `api` module re-exports all standardization components.
- **Sibling**: `api/documentation` consumes endpoint metadata for OpenAPI generation.
- **Consumers**: Any module building HTTP or GraphQL interfaces.

## Navigation

- **Parent**: [api/README.md](../README.md)
- **Sibling**: [SPEC.md](SPEC.md) | [README.md](README.md)
- **Root**: [../../../../README.md](../../../../README.md)
