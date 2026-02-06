# Compression Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Data compression with multiple algorithms: gzip, bzip2, lzma, zstd.

## Key Features

- **Multi-Algorithm** — gzip, bz2, lzma, zstd
- **Streaming** — Stream compression
- **Auto-Detect** — Auto-detect format
- **Level Control** — Compression levels

## Quick Start

```python
from codomyrmex.compression import compress, decompress

# Compress data
compressed = compress(data, algorithm="gzip", level=9)

# Decompress (auto-detect)
original = decompress(compressed)

# Stream compression
with compress_stream("out.gz", "gzip") as f:
    f.write(large_data)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/compression/](../../../src/codomyrmex/compression/)
- **Parent**: [Modules](../README.md)
