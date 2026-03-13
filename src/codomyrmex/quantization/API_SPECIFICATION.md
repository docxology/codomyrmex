# Quantization - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `quantization` module provides Int8 and FP4 (4-bit float) quantization for neural network weights. Supports symmetric/asymmetric Int8 quantization and FP4 quantization with nibble-packed storage, plus error metrics utilities.

## 2. Core Components

### 2.1 Int8 Quantization

| Class/Function | Description |
|----------------|-------------|
| `Int8Quantizer` | Configurable Int8 quantizer (symmetric/asymmetric, per-tensor/per-channel) |
| `QuantizedTensor` | Container for Int8 quantized data with scale and zero-point |
| `quantize_int8` | `(tensor, symmetric=True) -> QuantizedTensor` — Quantize float tensor to Int8 |
| `dequantize_int8` | `(qtensor) -> ndarray` — Restore float tensor from Int8 |

### 2.2 FP4 Quantization

| Class/Function | Description |
|----------------|-------------|
| `FP4Quantizer` | 4-bit floating-point quantizer with nibble packing |
| `FP4Tensor` | Container for FP4 quantized data |
| `quantize_fp4` | `(tensor) -> FP4Tensor` — Quantize float tensor to FP4 |
| `dequantize_fp4` | `(fp4_tensor) -> ndarray` — Restore float tensor from FP4 |

### 2.3 Utilities

| Function | Signature | Description |
|----------|-----------|-------------|
| `compute_scale_zero_point` | `(tensor, bits, symmetric) -> tuple` | Compute quantization parameters |
| `per_channel_scale` | `(tensor, axis, bits) -> ndarray` | Compute per-channel scales |
| `quantization_error` | `(original, dequantized) -> dict` | Compute MSE, max error, and SNR |

## 3. Usage Example

```python
from codomyrmex.quantization import quantize_int8, dequantize_int8, quantization_error
import numpy as np

weights = np.random.randn(256, 256).astype(np.float32)
qtensor = quantize_int8(weights, symmetric=True)
restored = dequantize_int8(qtensor)

error = quantization_error(weights, restored)
print(f"MSE: {error['mse']:.6f}, SNR: {error['snr_db']:.1f} dB")
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [MCP Tools](MCP_TOOL_SPECIFICATION.md)
