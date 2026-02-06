# Agent Guidelines - Compression

## Module Overview

Data compression with gzip, zlib, ZIP, and Zstandard support.

## Key Classes

- **Compressor** — Configurable compression with format detection
- **ArchiveManager** — ZIP/tar archive creation and extraction
- **ZstdCompressor** — High-performance Zstandard compression
- **ParallelCompressor** — Multi-threaded compression

## Agent Instructions

1. **Choose format wisely** — Use gzip for general, zstd for performance
2. **Use appropriate level** — Higher levels = slower but smaller
3. **Stream large files** — Use streaming for memory efficiency
4. **Handle errors** — Catch `CompressionError` for corrupt data
5. **Use parallel for batches** — `ParallelCompressor` for multiple files

## Common Patterns

```python
from codomyrmex.compression import compress, decompress, ArchiveManager

# Compress data
compressed = compress(data, level=6, format="gzip")

# Create archive with multiple files
with ArchiveManager("output.zip", mode="w") as archive:
    for file in files:
        archive.add_file(file)

# High-performance for large data
from codomyrmex.compression import ZstdCompressor
zstd = ZstdCompressor(level=3)
result = zstd.compress(large_data)
```

## Testing Patterns

```python
# Verify round-trip
from codomyrmex.compression import compress, decompress

data = b"test data " * 100
compressed = compress(data)
decompressed = decompress(compressed)
assert decompressed == data

# Verify compression ratio
assert len(compressed) < len(data)
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
