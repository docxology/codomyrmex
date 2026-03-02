# Quantization Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Numpy-only library for quantizing neural network weights and activations to lower bit-widths. Supports Int8 (symmetric and asymmetric) and FP4 (4-bit float with nibble packing).

## Features

- **Int8 Quantization**: Symmetric and asymmetric schemes with per-tensor and per-channel support
- **FP4 Quantization**: 16 representable float values, nibble-packed (2 values per byte) for 8x compression
- **Error Metrics**: Max/mean absolute error, relative error, and SNR in dB
- **Stateful Quantizers**: Calibrate-then-quantize workflow for production use
- **MCP Tools**: Auto-discovered `quantize_tensor` and `quantization_benchmark` tools

## Quick Start

```python
import numpy as np
from codomyrmex.quantization import quantize_int8, dequantize_int8, quantization_error

# Quantize a weight tensor
weights = np.random.randn(512, 256).astype(np.float32)
qt = quantize_int8(weights, scheme="symmetric")

# Reconstruct
reconstructed = dequantize_int8(qt)
error = quantization_error(weights, reconstructed)
print(f"Relative error: {error['relative_error']:.4f}")
print(f"SNR: {error['snr_db']:.1f} dB")
```

```python
from codomyrmex.quantization import quantize_fp4, dequantize_fp4

# FP4 for aggressive compression (8x vs float32)
ft = quantize_fp4(weights)
reconstructed = dequantize_fp4(ft)
print(f"Packed size: {ft.packed.nbytes} bytes (was {weights.nbytes})")
```

## Dependencies

- `numpy` (core dependency, no optional extras required)

## Module Structure

| File | Description |
|------|-------------|
| `int8.py` | Int8 quantization (QuantizedTensor, quantize/dequantize, Int8Quantizer) |
| `fp4.py` | FP4 quantization (FP4Tensor, quantize/dequantize, FP4Quantizer) |
| `utils.py` | Scale/zero-point computation, per-channel scaling, error metrics |
| `mcp_tools.py` | MCP-discoverable tool wrappers |

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Related**: [compression](../compression/README.md), [model_ops](../model_ops/README.md)
