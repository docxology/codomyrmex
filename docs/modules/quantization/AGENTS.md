# Quantization -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Int8 and FP4 (4-bit float) quantization for neural network weights. Supports symmetric and asymmetric Int8 quantization with nibble-packed FP4 storage, plus error metrics for quality assessment.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `quantize_tensor` | Quantize a list of float values to int8 or fp4 with error metrics | Standard | quantization |
| `quantization_benchmark` | Benchmark int8 vs fp4 quantization error on random data | Standard | quantization |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Quantize model weights for reduced memory and faster inference |
| VERIFY | QA Agent | Measure quantization error and compare methods |


## Agent Instructions

1. Int8 supports 'symmetric' and 'asymmetric' schemes; asymmetric has lower error for skewed distributions
2. FP4 achieves 8x compression vs float32 with higher error than int8


## Navigation

- [Source README](../../src/codomyrmex/quantization/README.md) | [SPEC.md](SPEC.md)
