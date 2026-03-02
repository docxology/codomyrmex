# Matmul Kernel Module -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Access Matrix

This document defines which PAI agent types can access matmul_kernel tools and at what trust level.

### Engineer Agent

**Access**: Full access to all tools
**Trust Level**: TRUSTED

| Tool | Capabilities |
|------|-------------|
| `matmul_compute` | Compute matrix products with configurable tile sizes |
| `matmul_benchmark` | Run performance benchmarks comparing tiled vs BLAS |

**Use Cases**: Numerical computation pipelines, performance analysis, algorithm prototyping.

### Architect Agent

**Access**: Read-only benchmarking
**Trust Level**: OBSERVED

| Tool | Capabilities |
|------|-------------|
| `matmul_benchmark` | Evaluate performance characteristics for architecture decisions |

**Use Cases**: Evaluating compute performance tradeoffs, sizing hardware requirements.

### QATester Agent

**Access**: Correctness validation
**Trust Level**: OBSERVED

| Tool | Capabilities |
|------|-------------|
| `matmul_compute` | Validate correctness of matrix operations against numpy reference |
| `matmul_benchmark` | Verify performance regression bounds |

**Use Cases**: Numerical accuracy testing, performance regression detection.

## Trust Levels

| Level | Description |
|-------|-------------|
| TRUSTED | Full read/write access to all module capabilities |
| OBSERVED | Read-only access, results logged for audit |
| UNTRUSTED | No access |
