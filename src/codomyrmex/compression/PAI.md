# Personal AI Infrastructure — Compression Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Compression module provides PAI integration for data compression.

## PAI Capabilities

### Data Compression

Compress data:

```python
from codomyrmex.compression import compress, decompress

compressed = compress(data, algorithm="gzip", level=9)
original = decompress(compressed)
```

### Stream Compression

Stream large data:

```python
from codomyrmex.compression import CompressStream

with CompressStream("output.gz", algorithm="gzip") as f:
    f.write(large_data)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `compress` | Compress data |
| `decompress` | Decompress data |
| `CompressStream` | Streaming |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
