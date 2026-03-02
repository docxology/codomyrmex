# AI Gateway Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

Load balancing, failover, and circuit breaker for LLM providers.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **EXECUTE** | Route LLM requests with failover and load balancing | `gateway_complete` |
| **OBSERVE** | Check provider health and circuit states | `gateway_health` |

## Installation

```bash
uv sync
```

## Key Exports

### Classes

- **`AIGateway`** -- Multi-provider gateway with load balancing and circuit breaking
- **`Provider`** -- LLM provider endpoint configuration
- **`CircuitBreaker`** -- Per-provider circuit breaker (closed/open/half-open)
- **`GatewayConfig`** -- Gateway configuration (strategy, thresholds)

## Quick Start

```python
from codomyrmex.ai_gateway import AIGateway, Provider, GatewayConfig

providers = [
    Provider(name="openai", endpoint="https://api.openai.com/v1", weight=2.0),
    Provider(name="anthropic", endpoint="https://api.anthropic.com/v1", weight=1.0),
]
config = GatewayConfig(strategy="weighted")
gateway = AIGateway(providers, config)

result = gateway.complete("Explain SLERP interpolation")
print(result["provider"], result["latency_ms"])
```

## Directory Structure

- `gateway.py` -- Core gateway, provider, circuit breaker, and config classes
- `mcp_tools.py` -- MCP tool definitions
- `__init__.py` -- Public API re-exports

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/ai_gateway/ -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
