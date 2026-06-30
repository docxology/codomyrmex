# AI Gateway - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `ai_gateway` module provides load balancing, automatic failover, and circuit breaking for LLM provider endpoints. Routes requests across multiple providers with configurable strategies and per-provider failure isolation.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `AIGateway` | Multi-provider gateway with routing, failover, and metrics tracking |
| `Provider` | Dataclass configuring a single LLM provider endpoint (name, endpoint, weight, timeout) |
| `CircuitBreaker` | Per-provider circuit breaker with closed/open/half-open state machine |
| `GatewayConfig` | Configuration dataclass for strategy, thresholds, and retry behaviour |

### 2.2 Key Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `AIGateway.complete` | `(prompt: str) -> dict` | Route a completion request to the best available provider |
| `AIGateway.health_check` | `() -> dict` | Return health status and metrics for all providers |
| `CircuitBreaker.call` | `(fn: Callable, *args, **kwargs) -> Any` | Execute function through circuit breaker |
| `CircuitBreaker.is_available` | `@property -> bool` | Whether the breaker allows requests |

## 3. MCP Tools

| Tool | Description |
|------|-------------|
| `gateway_complete` | Route a completion request through the AI Gateway with load balancing |
| `gateway_health` | Check health status of all configured providers |

## 4. Usage Example

```python
from codomyrmex.ai_gateway import AIGateway, GatewayConfig, Provider

providers = [
    Provider(name="openai", endpoint="https://api.openai.com/v1", weight=2.0),
    Provider(name="anthropic", endpoint="https://api.anthropic.com", weight=1.0),
]
gateway = AIGateway(providers, GatewayConfig(strategy="weighted"))

result = gateway.complete("Explain circuit breakers")
print(result["provider"], result["latency_ms"])
```

## 5. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [MCP Tools](MCP_TOOL_SPECIFICATION.md)
