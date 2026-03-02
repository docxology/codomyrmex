# Quantization Module -- PAI Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## PAI Algorithm Phase Mapping

### OBSERVE Phase

- **Error Analysis**: Use `quantization_error()` to observe the accuracy impact of existing quantized models.
- **Benchmark Comparison**: Use `quantization_benchmark` MCP tool to survey int8 vs fp4 trade-offs on representative data.

### THINK Phase

- **Trade-off Evaluation**: Compare symmetric vs asymmetric int8 error profiles to reason about which scheme fits the data distribution.
- **Compression Planning**: Evaluate whether 8x FP4 compression is acceptable given the accuracy requirements.

### BUILD Phase

- **Int8 Quantization**: Use `quantize_int8()` with symmetric or asymmetric scheme for weight quantization.
- **FP4 Quantization**: Use `quantize_fp4()` for aggressive compression where accuracy tolerates 4-bit representation.
- **Calibration**: Use `Int8Quantizer.calibrate()` with representative data for production quantization workflows.
- **Per-Channel**: Use `per_channel=True` for more accurate per-channel weight quantization.

### VERIFY Phase

- **Accuracy Validation**: Use `quantization_error()` to verify max/mean/relative error and SNR meet thresholds.
- **Roundtrip Testing**: Verify `dequantize(quantize(x))` produces acceptable reconstruction.
- **Benchmark**: Use `quantization_benchmark` to confirm performance characteristics.

## MCP Tools

Two tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `quantize_tensor` | Quantize float values to int8 or fp4, returns error metrics | Safe | quantization |
| `quantization_benchmark` | Benchmark int8 vs fp4 on random data | Safe | quantization |

## Agent Capabilities

| PAI Agent Type | Primary Functions | Use Case |
|----------------|------------------|----------|
| Engineer | quantize_int8, quantize_fp4, Int8Quantizer, FP4Quantizer | Implementing model compression |
| Architect | quantization_error, quantization_benchmark | Evaluating compression strategies |
| QATester | quantize_int8/fp4 + dequantize roundtrips, quantization_error | Accuracy regression testing |

## Trust Gateway

All quantization operations are read-only transformations on data provided by the caller. No destructive operations. All tools operate at SAFE trust level.
