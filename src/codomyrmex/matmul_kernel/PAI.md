# Matmul Kernel Module -- PAI Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## PAI Algorithm Phase Mapping

### BUILD Phase

**Tools**: `matmul_compute`

- Compute matrix products as part of numerical data pipelines
- Validate tiling algorithm correctness during implementation of GPU kernel prototypes

### VERIFY Phase

**Tools**: `matmul_benchmark`, `matmul_compute`

- Benchmark tiled matmul against NumPy BLAS to measure overhead
- Verify numerical correctness (max error < 1e-4 for float32)
- Detect performance regressions across matrix sizes

### EXECUTE Phase

**Tools**: `matmul_compute`

- Run matrix multiplications as part of agent computational workflows
- Provide matrix operation results to downstream modules

## MCP Tool Summary

| Tool | Category | Trust Required |
|------|----------|---------------|
| `matmul_compute` | matmul_kernel | OBSERVED |
| `matmul_benchmark` | matmul_kernel | OBSERVED |

## Integration Notes

- This module is compute-only with no side effects (no file I/O, no network)
- All tools are safe (read-only computation) and require no elevated trust
- NumPy is the only dependency (part of core codomyrmex dependencies)
