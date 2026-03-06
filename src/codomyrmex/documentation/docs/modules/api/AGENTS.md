# API -- Agent Integration Guide

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Agent Capabilities

The API module provides agents with tools to discover, document, and verify API infrastructure. Agents can list endpoints from source code, generate OpenAPI specifications, and check the health of API submodules.

## Available MCP Tools

### api_list_endpoints

Scan source code for API endpoint definitions using the documentation generator's code analysis.

**Parameters:**
- `source_path` (str, default: ".") -- Directory or file path to scan for API endpoints

**Returns:** Dictionary with discovered endpoint count and endpoint details.

### api_get_spec

Generate an API specification from source code analysis.

**Parameters:**
- `title` (str, default: "Codomyrmex API") -- Title for the generated API documentation
- `version` (str, default: "1.0.0") -- API version string
- `source_paths` (str, default: "") -- Comma-separated list of source directories to scan
- `base_url` (str, default: "") -- Base URL for the API

**Returns:** Dictionary with the generated API specification.

### api_health_check

Verify that all core API submodules can be imported successfully.

**Parameters:** None

**Returns:** Dictionary with health status per submodule (documentation, standardization, authentication, rate_limiting, circuit_breaker, webhooks, mocking, pagination).

## Agent Interaction Patterns

### OBSERVE Phase
Use `api_health_check` to verify module readiness. Use `api_list_endpoints` to discover existing API surface before making changes.

### BUILD Phase
Use `api_get_spec` to generate OpenAPI specifications after implementing new endpoints. The generated spec can be used for documentation and client generation.

## Trust Level

All three MCP tools are classified as **Safe** -- they perform read-only operations.

## Navigation

- **Source**: [src/codomyrmex/api/](../../../../src/codomyrmex/api/)
- **Extended README**: [README.md](readme.md)
- **SPEC**: [SPEC.md](SPEC.md)
- **Parent**: [All Modules](../README.md)
