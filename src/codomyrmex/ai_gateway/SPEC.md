# AI Gateway - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Route LLM requests across multiple providers with load balancing, automatic failover, and circuit breaking to prevent cascade failures.

## Functional Requirements

- Round-robin and weighted load balancing strategies
- Per-provider circuit breaker with closed/open/half-open states
- Automatic failover to healthy providers on failure
- Request metrics tracking (count, failures, latency)
- Provider health checking

## Core Classes

| Class | Description |
|-------|-------------|
| `AIGateway` | Multi-provider gateway with routing and metrics |
| `Provider` | Provider endpoint configuration |
| `CircuitBreaker` | Per-provider failure isolation |
| `GatewayConfig` | Strategy and threshold settings |

## Circuit Breaker States

| State | Behavior |
|-------|----------|
| CLOSED | Normal operation, requests pass through |
| OPEN | Requests rejected, waiting for recovery timeout |
| HALF_OPEN | Allowing one test request to check recovery |

## Design Principles

1. **Fail fast** -- Circuit breaker prevents slow failures from blocking
2. **Automatic recovery** -- Half-open state tests provider recovery
3. **No silent fallbacks** -- All failures are explicit in return values
4. **Strategy extensible** -- New load balancing strategies via config

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
