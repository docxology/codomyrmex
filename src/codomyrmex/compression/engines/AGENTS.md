# Codomyrmex Agents — src/codomyrmex/compression/engines

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Compression engine implementations providing multi-threaded parallel compression with progress tracking and statistics, plus a high-performance Zstandard compressor. Supports chunked large-data compression with split-and-merge workflows.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `parallel.py` | `ParallelCompressor` | Multi-threaded batch compress/decompress via `ThreadPoolExecutor` with progress callbacks |
| `parallel.py` | `CompressionStats` | Statistics dataclass: input/output bytes, duration, ratio, throughput_mbps, savings_percent |
| `zstd_compressor.py` | `ZstdCompressor` | High-performance Zstandard compression with configurable level (requires `zstandard` package) |

## Operating Contracts

- `ParallelCompressor` preserves input order in output (indexed result array).
- `split_and_compress` splits data into configurable chunks (default 1MB) for parallel processing.
- `decompress_and_merge` reverses `split_and_compress` by decompressing and concatenating.
- `CompressionStats` is computed after every batch operation and available via `last_stats` property.
- `ZstdCompressor` raises `ImportError` at construction if `zstandard` package is not installed.
- `ZstdCompressor.compress` accepts an optional `level` override per call (default uses constructor level).
- Errors must be logged before re-raising.

## Integration Points

- **Depends on**: `compression.core.compressor.Compressor` (base compressor for format dispatch)
- **Used by**: `compression` parent module, data pipeline compression, backup systems
- **External**: `zstandard` (optional, for `ZstdCompressor`)

## Navigation

- **Parent**: [compression](../README.md)
- **Root**: [Root](../../../../README.md)
