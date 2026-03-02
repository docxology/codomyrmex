# Quantization Module -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Access Matrix

### Engineer Agent

**Access**: Full access to all quantization functions
**Trust Level**: TRUSTED

| Function | Capabilities |
|----------|-------------|
| `quantize_int8` | Quantize weight tensors to int8 (symmetric/asymmetric) |
| `quantize_fp4` | Quantize to FP4 with nibble packing |
| `Int8Quantizer` | Calibrate and quantize with stateful workflow |
| `FP4Quantizer` | Stateful FP4 quantization |

**Use Cases**: Model compression, inference optimization, weight quantization pipelines.

### Architect Agent

**Access**: Read-only analysis, error evaluation
**Trust Level**: OBSERVED

| Function | Capabilities |
|----------|-------------|
| `quantization_error` | Evaluate accuracy/compression trade-offs |
| `compute_scale_zero_point` | Understand quantization parameters |

**Use Cases**: Architecture decisions on quantization strategy, accuracy vs size trade-off analysis.

### QATester Agent

**Access**: Validation and error measurement
**Trust Level**: OBSERVED

| Function | Capabilities |
|----------|-------------|
| `quantize_int8` / `dequantize_int8` | Roundtrip validation |
| `quantize_fp4` / `dequantize_fp4` | Roundtrip validation |
| `quantization_error` | Accuracy regression testing |
| `quantization_benchmark` | Performance benchmarking |

**Use Cases**: Quantization accuracy regression tests, roundtrip correctness validation.

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `quantize_tensor` | Quantize a list of float values to int8 or fp4 | SAFE |
| `quantization_benchmark` | Benchmark int8 vs fp4 on random data | SAFE |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `quantize_tensor`, `quantization_benchmark` | TRUSTED |
| **Architect** | Analysis | `quantization_benchmark` -- trade-off evaluation | OBSERVED |
| **QATester** | Validation | `quantize_tensor`, `quantization_benchmark` -- accuracy testing | OBSERVED |
| **Researcher** | Read-only | `quantization_benchmark` -- comparison data | SAFE |
