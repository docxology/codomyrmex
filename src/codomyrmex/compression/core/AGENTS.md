# Codomyrmex Agents -- src/codomyrmex/compression/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides the core data compression and decompression engine supporting gzip, zlib, and ZIP formats. Offers both in-memory and file-based compression with configurable levels, stream support, automatic format detection via magic bytes, and a format comparison utility.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `compressor.py` | `Compressor` | Main compression class supporting gzip, zlib, and ZIP with configurable levels (0-9) |
| `compressor.py` | `Compressor.compress` / `decompress` | In-memory byte-level compression and decompression |
| `compressor.py` | `Compressor.compress_file` / `decompress_file` | File-based compression with automatic output path inference |
| `compressor.py` | `Compressor.compress_stream` / `decompress_stream` | Stream-based IO compression |
| `compressor.py` | `Compressor.detect_format` | Detects compression format from data via magic byte inspection |
| `compressor.py` | `compress_data` / `decompress_data` | Convenience one-shot functions |
| `compressor.py` | `auto_decompress` | Detects format automatically and decompresses |
| `compressor.py` | `compare_formats` | Benchmarks all supported formats returning size, ratio, and timing metrics |
| `compressor.py` | `CompressionError` | Domain-specific error for compression failures |

## Operating Contracts

- Supported formats are defined in `Compressor.SUPPORTED_FORMATS`: `{"gzip", "zlib", "zip"}`.
- Compression level ranges from 0 (no compression) to 9 (maximum), defaulting to 6.
- Format detection uses magic byte prefixes: `\x1f\x8b` (gzip), `PK` (ZIP), `\x78\x01/\x9c/\xda` (zlib).
- All errors are logged via `logging_monitoring` before being re-raised as `CompressionError`.
- File compression logs the percentage reduction achieved.
- `auto_decompress` raises `CompressionError` when format cannot be determined.

## Integration Points

- **Depends on**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: `compression.archives`, `compression.engines`, backup and artifact workflows

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
