# Quantization Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Int8 and FP4 (4-bit float) quantization for neural network weights. Supports symmetric and asymmetric Int8 quantization with nibble-packed FP4 storage, plus error metrics for quality assessment.

The optional native Apple MLX backend (`codomyrmex.quantization.mlx_quantizer`)
is disabled during ordinary discovery and test collection. Set
`RUN_LIVE_MLX=1` only for an explicitly verified local MLX runtime; this lane is
hardware/backend dependent and is not required for the portable Int8/FP4 API.

## Functional Requirements

1. Symmetric and asymmetric Int8 quantization with per-tensor scale and zero-point
2. FP4 quantization with nibble-packed storage (8x compression ratio)
3. Quantization error metrics: MSE, max absolute error, and SQNR


## Interface

```python
from codomyrmex.quantization import quantize_int8, dequantize_int8, quantize_fp4, dequantize_fp4, quantization_error

qt = quantize_int8(weights, scheme="asymmetric")
reconstructed = dequantize_int8(qt)
error = quantization_error(weights, reconstructed)
```

## Exports

Int8Quantizer, QuantizedTensor, quantize_int8, dequantize_int8, FP4Quantizer, FP4Tensor, quantize_fp4, dequantize_fp4, compute_scale_zero_point, per_channel_scale, quantization_error

## Navigation

- [Source README](../../../src/codomyrmex/quantization/README.md) | [AGENTS.md](AGENTS.md)
