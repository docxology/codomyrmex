# compression

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The compression module provides data compression utilities and archive handling with support for gzip, zlib, ZIP, and Zstandard formats. It offers configurable compression levels, automatic format detection via magic bytes, stream-based compression, file-level operations, and parallel batch compression using thread pools.

## Key Exports

### Classes

- **`Compressor`** -- Core compressor supporting gzip, zlib, and ZIP formats with configurable compression levels. Provides `compress()`, `decompress()`, `compress_file()`, and `decompress_file()` methods.
- **`ArchiveManager`** -- Handles archive creation and extraction for tar and zip formats.
- **`CompressionError`** -- Exception raised when compression or decompression operations fail. Extends `CodomyrmexError`.
- **`ZstdCompressor`** -- High-performance compressor using the Zstandard algorithm (requires `zstandard` package). Supports configurable compression levels.
- **`ParallelCompressor`** -- Compresses and decompresses multiple data chunks in parallel using `ThreadPoolExecutor` with configurable worker count.

### Functions

- **`compress()`** -- Compress data bytes with configurable level and format (defaults to gzip level 6).
- **`decompress()`** -- Decompress data bytes with optional format specification.
- **`get_compressor()`** -- Factory function returning a `Compressor` instance for the specified format.
- **`compress_data()`** -- Lower-level data compression from the compressor module.
- **`decompress_data()`** -- Lower-level data decompression from the compressor module.
- **`auto_decompress()`** -- Automatically detect format and decompress data using magic byte inspection.
- **`compress_file()`** -- Compress a file on disk with configurable format and level, returning the output path.
- **`decompress_file()`** -- Decompress a file on disk with configurable format, returning the output path.

## Directory Contents

- `__init__.py` - Module entry point with convenience functions and all exports
- `compressor.py` - `Compressor` class and `CompressionError` with gzip/zlib/ZIP support and magic byte detection
- `archive_manager.py` - `ArchiveManager` for tar and zip archive operations
- `zstd_compressor.py` - `ZstdCompressor` using the Zstandard algorithm (optional dependency)
- `parallel.py` - `ParallelCompressor` for multi-threaded batch compression/decompression
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/compression/](../../../docs/modules/compression/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
