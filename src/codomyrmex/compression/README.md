# Compression Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Compression module provides data compression utilities and archive handling for Codomyrmex, supporting multiple compression formats with configurable levels and stream-based processing.

## Key Features

- **Multiple Formats**: gzip, zlib, and ZIP support
- **Configurable Levels**: Balance between speed and compression ratio
- **Stream-Based Processing**: Memory-efficient compression for large files
- **Auto-Detection**: Automatically detect compression format
- **Archive Management**: Create and extract ZIP archives
- **File Utilities**: Direct file compression/decompression

## Quick Start

```python
from codomyrmex.compression import (
    compress, decompress, get_compressor,
    Compressor, ArchiveManager,
    compress_data, decompress_data, auto_decompress,
)

# Simple compression/decompression
data = b"This is some data to compress" * 100
compressed = compress(data, level=6, format="gzip")
original = decompress(compressed, format="gzip")

# Auto-detect format when decompressing
original = auto_decompress(compressed)

# Using the Compressor class
compressor = get_compressor(format="gzip")
compressed = compressor.compress(data, level=9)  # Max compression
original = compressor.decompress(compressed)

# Archive management
archive = ArchiveManager()
archive.create("output.zip", ["file1.txt", "file2.txt", "dir/"])
archive.extract("output.zip", "extracted/")
archive.list_contents("output.zip")
```

## Core Classes

| Class | Description |
|-------|-------------|
| `Compressor` | Core compression/decompression operations |
| `ArchiveManager` | Create, extract, and manage archives |

## Formats

| Format | Use Case |
|--------|----------|
| `gzip` | General-purpose, good balance of speed/ratio |
| `zlib` | Raw deflate compression |
| `zip` | Multi-file archives with directory structure |

## Compression Levels

| Level | Description |
|-------|-------------|
| 0 | No compression (store only) |
| 1-3 | Fast compression, lower ratio |
| 4-6 | Balanced (default: 6) |
| 7-9 | Maximum compression, slower |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `compress(data, level, format)` | Compress bytes data |
| `decompress(data, format)` | Decompress bytes data |
| `get_compressor(format)` | Get a Compressor instance |
| `auto_decompress(data)` | Decompress with auto-detection |
| `compress_data(data)` | Quick compress helper |
| `decompress_data(data)` | Quick decompress helper |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `CompressionError` | Compression operations failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
