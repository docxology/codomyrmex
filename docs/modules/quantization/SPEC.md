# Quantization Specification

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides Int8 and FP4 (4-bit float) quantization for neural network weights. Supports symmetric and asymmetric Int8 quantization with nibble-packed FP4 storage, plus error metrics for quality assessment.

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

- [Source README](../../src/codomyrmex/quantization/README.md) | [AGENTS.md](AGENTS.md)
