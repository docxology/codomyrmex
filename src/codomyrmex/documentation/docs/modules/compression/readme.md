# Compression Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Data compression utilities with gzip, zlib, ZIP, and Zstandard support.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Compress build artifacts and archive outputs | Direct Python import |
| **EXECUTE** | Compress and decompress data during pipeline runs | Direct Python import |
| **VERIFY** | Validate compression ratios and archive integrity | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses it during BUILD phase to compress artifacts, and during EXECUTE phase to handle data compression in processing pipelines.

## Key Exports

### Functions
- **`compress()`** — Compress data.
- **`decompress()`** — Decompress data.
- **`get_compressor()`** — Get a compressor instance.
- **`compress_file()`** — Compress a file.
- **`decompress_file()`** — Decompress a file.

## Quick Start

```python
from codomyrmex.compression import (
    compress, decompress, compress_file, decompress_file,
    Compressor, ArchiveManager, ZstdCompressor, ParallelCompressor
)

# Compress data
data = b"Hello, World! " * 1000
compressed = compress(data, level=6, format="gzip")
print(f"Ratio: {len(data) / len(compressed):.1f}x")

# Decompress
original = decompress(compressed)

# Compress a file
output_path = compress_file("data.json", format="gzip")

# Create archives
with ArchiveManager("backup.zip", mode="w") as archive:
    archive.add_file("file1.txt")
    archive.add_directory("data/")

# High-performance compression
zstd = ZstdCompressor(level=3)
fast_compressed = zstd.compress(data)

# Parallel compression for large data
parallel = ParallelCompressor(workers=4)
result = parallel.compress_files(["file1.txt", "file2.txt"])
```

## Exports

| Item | Description |
|------|-------------|
| `compress(data, level, format)` | Compress bytes |
| `decompress(data, format)` | Decompress bytes |
| `compress_file(path, format)` | Compress file |
| `decompress_file(path)` | Decompress file |
| `Compressor` | Configurable compressor class |
| `ArchiveManager` | ZIP/tar archive handling |
| `ZstdCompressor` | High-performance Zstandard |
| `ParallelCompressor` | Multi-threaded compression |
| `CompressionError` | Compression exception |

## Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| gzip | .gz | General purpose |
| zlib | .zz | Data streams |
| zip | .zip | Archives |
| zstd | .zst | High performance |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k compression -v
```

## Documentation

- [Module Documentation](../../../docs/modules/compression/README.md)
- [Agent Guide](../../../docs/modules/compression/AGENTS.md)
- [Specification](../../../docs/modules/compression/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
