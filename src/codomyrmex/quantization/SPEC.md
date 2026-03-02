# Quantization Module -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Quantization Schemes

### Int8 Symmetric

Maps the float range [-|x|_max, |x|_max] to [-127, 127].

| Parameter | Value |
|-----------|-------|
| Bit width | 8 |
| Range | [-127, 127] |
| Zero point | 0 (always) |
| Scale | max(abs(x)) / 127 |
| Clamp range | [-127, 127] |

Formula:
- Quantize: `q = clamp(round(x / scale), -127, 127)`
- Dequantize: `x_approx = q * scale`

### Int8 Asymmetric

Maps the float range [x_min, x_max] to [-128, 127].

| Parameter | Value |
|-----------|-------|
| Bit width | 8 |
| Range | [-128, 127] |
| Scale | (x_max - x_min) / 255 |
| Zero point | clamp(round(-128 - x_min / scale), -128, 127) |
| Clamp range | [-128, 127] |

Formula:
- Quantize: `q = clamp(round(x / scale) + zero_point, -128, 127)`
- Dequantize: `x_approx = (q - zero_point) * scale`

### FP4 (4-bit Float)

Format: 1 sign bit, 1 exponent bit, 2 mantissa bits.

| Parameter | Value |
|-----------|-------|
| Bit width | 4 |
| Representable values | 16 |
| Value set (positive) | {0, 0.0625, 0.125, 0.25, 0.5, 1.0, 1.5, 2.0} |
| Value set (negative) | {-0, -0.0625, -0.125, -0.25, -0.5, -1.0, -1.5, -2.0} |
| Storage | Nibble-packed uint8 (2 values per byte) |
| Compression ratio | 8x vs float32 |
| Global scale | max(abs(x)) / 2.0 |

Packing format:
- Lower nibble (bits 0-3): first FP4 index
- Upper nibble (bits 4-7): second FP4 index
- Odd-length arrays: last byte has 0 in upper nibble

## Error Metrics

| Metric | Formula |
|--------|---------|
| Max absolute error | max(abs(original - reconstructed)) |
| Mean absolute error | mean(abs(original - reconstructed)) |
| Relative error | mean_abs_error / (mean(abs(original)) + 1e-8) |
| SNR (dB) | 10 * log10(mean(original^2) / (mean(diff^2) + 1e-10)) |

## Interface Contracts

### Int8 Quantization

```python
def quantize_int8(x: np.ndarray, scheme: str = "asymmetric",
                  per_channel: bool = False, axis: int = 0) -> QuantizedTensor
def dequantize_int8(qt: QuantizedTensor) -> np.ndarray
def compute_scale_zero_point_int8(x: np.ndarray, scheme: str = "asymmetric",
                                   axis: int | None = None) -> tuple[float | np.ndarray, int | np.ndarray]
```

### FP4 Quantization

```python
def quantize_fp4(x: np.ndarray) -> FP4Tensor
def dequantize_fp4(ft: FP4Tensor) -> np.ndarray
```

### Utilities

```python
def compute_scale_zero_point(x_min: float, x_max: float, n_bits: int = 8,
                              scheme: str = "asymmetric") -> tuple[float, int]
def per_channel_scale(x: np.ndarray, axis: int = 0) -> np.ndarray
def quantization_error(original: np.ndarray, reconstructed: np.ndarray) -> dict
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | >= 1.24 | Core tensor operations |

## Navigation

- **Parent**: [codomyrmex](../SPEC.md)
- **Related**: [compression](../compression/SPEC.md), [model_ops](../model_ops/SPEC.md)
