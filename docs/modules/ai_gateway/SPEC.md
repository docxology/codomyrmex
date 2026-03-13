# AI Gateway Specification

**Version**: v1.2.2 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides load balancing, failover, and circuit breaker patterns for LLM provider management. Routes completion requests across multiple AI providers with configurable strategies.

## Functional Requirements

1. Load balance completion requests across multiple LLM providers using configurable strategies (round_robin, weighted)
2. Circuit breaker pattern with automatic failover when a provider becomes unhealthy
3. Health monitoring for all registered providers with state reporting


## Interface

```python
from codomyrmex.ai_gateway import AIGateway, Provider, GatewayConfig

providers = [Provider(name="openai", endpoint="...", weight=1.0)]
config = GatewayConfig(strategy="round_robin")
gateway = AIGateway(providers, config)
result = gateway.complete("prompt text")
health = gateway.health_check()
```

## Exports

AIGateway, Provider, CircuitBreaker, GatewayConfig

## Navigation

- [Source README](../../src/codomyrmex/ai_gateway/README.md) | [AGENTS.md](AGENTS.md)
