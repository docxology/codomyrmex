# Matrix Multiplication Kernel -- Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a tiled (cache-efficient) matrix multiplication kernel in pure Python/NumPy. Implements BLAS-style blocked matmul for improved cache locality, plus batched multiplication and FLOP counting.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `matmul_compute` | Multiply two matrices using tiled algorithm and verify against NumPy | Standard | matmul_kernel |
| `matmul_benchmark` | Benchmark tiled matmul against NumPy for various matrix sizes | Standard | matmul_kernel |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Perform matrix multiplications with cache-efficient tiling |
| VERIFY | QA Agent | Benchmark tiled matmul correctness and performance vs NumPy |


## Agent Instructions

1. tile_size controls cache block size (default 32); adjust for target cache hierarchy
2. max_size capped at 512 for matmul_benchmark to keep execution time reasonable


## Navigation

- [Source README](../../src/codomyrmex/matmul_kernel/README.md) | [SPEC.md](SPEC.md)
