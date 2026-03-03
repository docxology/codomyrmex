# Compression

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Compression module provides data compression utilities and archive handling for the codomyrmex platform. It supports gzip, zlib, ZIP, and Zstandard formats with configurable compression levels, stream-based compression, automatic format detection, parallel compression, and file-level operations.

## Architecture Overview

```
compression/
├── __init__.py              # Public API (compress, decompress, get_compressor, file ops)
├── core/
│   └── compressor.py        # Compressor class, compress_data, decompress_data, auto_decompress
├── archives/
│   └── archive_manager.py   # ArchiveManager for ZIP archive operations
└── engines/
    ├── parallel.py          # ParallelCompressor for multi-threaded compression
    └── zstd_compressor.py   # ZstdCompressor for Zstandard format
```

## Key Classes and Functions

**`Compressor`** -- Core compressor with format-aware compress/decompress methods.

**`ArchiveManager`** -- ZIP archive creation, extraction, and listing.

**`ZstdCompressor`** -- Zstandard high-performance compression.

**`ParallelCompressor`** -- Multi-threaded compression for large datasets.

### Convenience Functions

- `compress(data, level=6, format="gzip") -> bytes`
- `decompress(data, format=None) -> bytes`
- `compress_file(input_path, output_path, format, level) -> str`
- `decompress_file(input_path, output_path, format) -> str`
- `auto_decompress(data) -> bytes` -- Automatic format detection

## Usage Examples

```python
from codomyrmex.compression import compress, decompress

compressed = compress(b"Hello, World!", level=9, format="gzip")
original = decompress(compressed, format="gzip")

from codomyrmex.compression import compress_file
output = compress_file("large_data.csv", format="zstd")
```

## Error Handling

- `CompressionError` -- Base exception for compression failures

## Related Modules

- [`serialization`](../serialization/readme.md) -- Data serialization before compression

## Navigation

- **Source**: [src/codomyrmex/compression/](../../../../src/codomyrmex/compression/)
- **Parent**: [All Modules](../README.md)
