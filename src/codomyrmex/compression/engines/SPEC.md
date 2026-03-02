# Compression Engines — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Two compression engines: `ParallelCompressor` for multi-threaded batch compression with progress tracking and statistics, and `ZstdCompressor` for high-performance Zstandard compression.

## Architecture

`ParallelCompressor` delegates per-chunk compression to the `Compressor` class from `compression.core` and distributes work across a `ThreadPoolExecutor`. `ZstdCompressor` wraps the `zstandard` library directly.

## Key Classes

### `ParallelCompressor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compress_batch` | `data_list: list[bytes], on_progress: Callable \| None` | `list[bytes]` | Compress multiple blobs in parallel (order preserved) |
| `decompress_batch` | `data_list: list[bytes], on_progress: Callable \| None` | `list[bytes]` | Decompress multiple blobs in parallel |
| `split_and_compress` | `data: bytes, on_progress: Callable \| None` | `list[bytes]` | Split large data into chunks and compress each |
| `decompress_and_merge` | `compressed_chunks: list[bytes], on_progress` | `bytes` | Decompress chunks and concatenate |
| `last_stats` | property | `CompressionStats \| None` | Stats from most recent operation |

Constructor: `format: str = "gzip"`, `max_workers: int = 4`, `chunk_size: int = 1048576` (1MB)

### `CompressionStats` (dataclass)

| Field / Property | Type | Description |
|-----------------|------|-------------|
| `input_bytes` | `int` | Total input size |
| `output_bytes` | `int` | Total output size |
| `duration_seconds` | `float` | Wall-clock time |
| `chunk_count` | `int` | Number of chunks processed |
| `ratio` | `float` (property) | `output / input` (lower = better) |
| `throughput_mbps` | `float` (property) | MB/s throughput |
| `savings_percent` | `float` (property) | `(1 - ratio) * 100` |

### `ZstdCompressor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `compress` | `data: bytes, level: int \| None` | `bytes` | Compress with Zstd; optional level override (1-22) |
| `decompress` | `data: bytes` | `bytes` | Decompress Zstd data |

Constructor: `level: int = 3`. Raises `ImportError` if `zstandard` not installed.

## Dependencies

- **Internal**: `compression.core.compressor.Compressor`
- **External**: `zstandard` (optional, for `ZstdCompressor`); standard library (`concurrent.futures`, `time`)

## Constraints

- `ParallelCompressor` supported formats depend on `compression.core.compressor.Compressor` (gzip, bz2, lzma).
- `ZstdCompressor` requires `pip install zstandard`; raises `ImportError` otherwise.
- Progress callback signature: `on_progress(completed: int, total: int)`.
- Zero-mock: real compression only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ThreadPoolExecutor` futures propagate compression errors from worker threads.
- `ZstdCompressor` constructor validates `zstandard` availability at init time.
