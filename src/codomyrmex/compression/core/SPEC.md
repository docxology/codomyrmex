# Compression Core -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Core compression and decompression engine supporting gzip, zlib, and ZIP formats with configurable compression levels, stream-based IO, file-level operations, automatic format detection via magic bytes, and a multi-format benchmarking utility.

## Architecture

Single-class design with `Compressor` as the primary interface. Each instance is configured with a format at construction. Convenience module-level functions (`compress_data`, `decompress_data`, `auto_decompress`, `compare_formats`) wrap `Compressor` for one-shot use.

## Key Classes

### `Compressor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `format: str = "gzip"` | `None` | Initializes with format; raises `ValueError` for unsupported formats |
| `compress` | `data: bytes, level: int = 6` | `bytes` | Compresses in-memory data at the given level (0-9) |
| `decompress` | `data: bytes` | `bytes` | Decompresses in-memory data |
| `compress_stream` | `input_stream: IO[bytes], output_stream: IO[bytes], level: int = 6` | `None` | Stream-to-stream compression |
| `decompress_stream` | `input_stream: IO[bytes], output_stream: IO[bytes]` | `None` | Stream-to-stream decompression |
| `compress_file` | `input_path: str, output_path: str \| None, level: int = 6` | `str` | Compresses a file; returns output path; logs ratio |
| `decompress_file` | `input_path: str, output_path: str \| None` | `str` | Decompresses a file; infers output path from extension |
| `detect_format` | `data: bytes` | `str \| None` | Detects format from magic bytes |
| `get_compression_ratio` | `original: bytes, compressed: bytes` | `float` | Static method returning percentage reduction |

### Module-Level Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `compress_data` | `data, format, level` | `bytes` | One-shot compress |
| `decompress_data` | `data, format` | `bytes` | One-shot decompress |
| `auto_decompress` | `data` | `bytes` | Auto-detect format and decompress |
| `compare_formats` | `data, level` | `dict` | Benchmark all formats with size, ratio, time_ms |

### `CompressionError`

Inherits from `CodomyrmexError`. Raised for all compression and decompression failures.

## Dependencies

- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `gzip` (stdlib), `zlib` (stdlib), `zipfile` (stdlib)

## Constraints

- `SUPPORTED_FORMATS` is `{"gzip", "zlib", "zip"}`; any other format raises `ValueError` at construction.
- Magic byte detection: `\x1f\x8b` = gzip, `PK` = zip, `\x78\x01/\x9c/\xda` = zlib.
- `auto_decompress` raises `CompressionError` when format detection fails.
- Zero-mock: real compression only, `NotImplementedError` for unimplemented paths.

## Error Handling

- All exceptions are caught, logged via `logger.error`, and re-raised as `CompressionError` with exception chaining (`from e`).
