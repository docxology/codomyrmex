# Codomyrmex Agents -- src/codomyrmex/agents/infrastructure

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides a `BaseAgent` subclass specialized for cloud infrastructure operations. The module wraps Infomaniak cloud clients (compute, volume, network, S3, DNS, Heat orchestration) behind a JSON command-dispatch interface and auto-generates tool descriptors from client method signatures via `CloudToolFactory`.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `agent.py` | `InfrastructureAgent` | `BaseAgent` subclass that dispatches JSON `{"service", "action", ...params}` prompts to cloud clients |
| `agent.py` | `InfrastructureAgent.from_env` | Class method that creates an agent from environment variables, silently skipping unavailable clients |
| `agent.py` | `InfrastructureAgent.populate_tool_registry` | Auto-generates `Tool` objects from all registered client methods |
| `tool_factory.py` | `Tool` | Lightweight dataclass descriptor: name, description, JSON-schema parameters, callable handler |
| `tool_factory.py` | `CloudToolFactory` | Static factory that introspects client methods, extracts parameter schemas, and optionally wraps handlers with security pipeline checks |
| `tool_factory.py` | `_method_to_args_schema` | Converts a method signature into a JSON-schema-like parameter dict |

## Operating Contracts

- `_execute_impl` expects a JSON prompt with `service` and `action` keys; returns `AgentResponse` with JSON content or error.
- Security pipeline (`CloudSecurityPipeline`) runs `pre_check` before and `post_process` after every client call when configured.
- `CloudToolFactory._wrap_with_security` raises `PermissionError` if `pre_check.allowed` is False.
- Clients are lazily imported in `from_env` and silently skipped on `ImportError`, `OSError`, `ValueError`, or `AttributeError`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.agents.core.base` (`BaseAgent`, `AgentCapabilities`, `AgentRequest`, `AgentResponse`), `codomyrmex.cloud.infomaniak` (compute, volume, network, S3, DNS, Heat clients), `codomyrmex.cloud.infomaniak.security` (`CloudSecurityPipeline`)
- **Used by**: Cloud-facing agent workflows, PAI infrastructure operations

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [codomyrmex](../../../../README.md)
