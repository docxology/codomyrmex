# AI Gateway Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `ai_gateway` module. Covers provider configuration, gateway config defaults, circuit breaker state machine, multi-provider gateway routing and failover, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestProvider` | Provider creation with defaults and custom config |
| `TestGatewayConfig` | Gateway config defaults and custom settings |
| `TestCircuitBreaker` | Circuit breaker states (closed, open, half-open), recovery, re-opening |
| `TestAIGateway` | Round-robin routing, failover, health checks, metrics, unavailable providers |
| `TestAIGatewayMCPTools` | MCP tool functions (gateway_complete, gateway_health) |

## Test Structure

```
tests/unit/ai_gateway/
    __init__.py
    test_ai_gateway.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/ai_gateway/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/ai_gateway/ --cov=src/codomyrmex/ai_gateway -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../ai_gateway/README.md)
- [All Tests](../README.md)
