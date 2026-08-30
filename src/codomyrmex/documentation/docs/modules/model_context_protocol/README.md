<!-- readme: generated -->

# model_context_protocol

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/model_context_protocol/`

## Overview

Model Context Protocol Module for Codomyrmex.

The Model Context Protocol (MCP) is a foundational specification within the Codomyrmex
ecosystem, designed to standardize communication and interactions between different
components and external models.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available classes:
- MCPErrorDetail
- MCPToolCall
- MCPToolResult

## Public Exports

`model_context_protocol` exports 48 public symbols via `__all__`:

`CircuitBreaker`, `CircuitBreakerConfig`, `CircuitOpenError`, `CircuitState`, `DiscoveryMetrics`, `DiscoveryReport`, `FailedModule`, `FieldError`, `MCPClient`, `MCPClientConfig`, `MCPClientError`, `MCPDiscovery`, `MCPErrorCode`, `MCPErrorDetail`, `MCPMessage`, `MCPRegistrationError`, `MCPServer`, `MCPServerConfig`, `MCPToolCall`, `MCPToolError`, `MCPToolRegistry`, `MCPToolResult`, `RateLimiter`, `RateLimiterConfig` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../model_context_protocol/](../../../../model_context_protocol/)
