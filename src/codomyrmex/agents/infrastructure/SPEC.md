# Infrastructure -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Cloud infrastructure agent module that bridges the `BaseAgent` interface with Infomaniak cloud service clients. Provides JSON command dispatch, automatic tool registry generation via method introspection, and optional security pipeline integration for pre/post execution checks.

## Architecture

Follows the GitAgent pattern: a `BaseAgent` subclass receives structured JSON prompts, resolves a service client and action method, executes with extracted parameters, and returns a JSON `AgentResponse`. `CloudToolFactory` uses `inspect.signature` to auto-generate tool descriptors from client public methods.

## Key Classes

### `InfrastructureAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `clients: dict[str, Any]`, `security_pipeline: Any`, `config: dict` | `None` | Registers clients and optional security pipeline; sets `AgentCapabilities` |
| `from_env` | (classmethod) | `InfrastructureAgent` | Creates agent from env vars, attempting each Infomaniak client |
| `_execute_impl` | `request: AgentRequest` | `AgentResponse` | Parses JSON prompt, dispatches to client method, applies security checks |
| `stream` | `request: AgentRequest` | `Iterator[str]` | Yields single execute result (streaming not natively supported) |
| `populate_tool_registry` | `registry: dict[str, Tool] \| None` | `dict[str, Tool]` | Auto-generates Tool objects from all configured client methods |
| `available_services` | -- | `list[str]` | Returns names of configured service clients |
| `test_connection` | -- | `bool` | Validates connectivity to all configured clients |

### `Tool`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique tool identifier, format: `infomaniak_{service}_{method}` |
| `description` | `str` | `{service}.{method}` label |
| `parameters` | `dict[str, Any]` | JSON-schema-like parameter definition |
| `handler` | `Callable \| None` | Bound method or security-wrapped callable |

### `CloudToolFactory`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_client` | `client`, `service_name: str`, `registry: dict`, `security_pipeline` | `list[str]` | Registers all public methods of one client as `Tool` objects |
| `register_all_clients` | `registry: dict`, `clients: dict`, `security_pipeline` | `dict[str, list[str]]` | Batch registers tools from multiple service clients |

## Dependencies

- **Internal**: `codomyrmex.agents.core.base`, `codomyrmex.cloud.infomaniak` (6 client types), `codomyrmex.cloud.infomaniak.security`
- **External**: Standard library only (`inspect`, `json`, `logging`)

## Constraints

- JSON prompt must contain both `service` and `action` keys or the request is rejected.
- Only public, non-underscore-prefixed callable methods are registered as tools.
- Parameter type annotations default to `"string"` when absent or unrecognized.
- Zero-mock: real cloud clients required, `NotImplementedError` for unimplemented paths.

## Error Handling

- `json.JSONDecodeError` raised when prompt is not valid JSON.
- `PermissionError` raised by security wrapper when `pre_check` denies the action.
- `TypeError` raised when extracted params do not match client method signature.
- All errors logged via `logger.exception` before returning as `AgentResponse.error`.
