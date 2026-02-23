# Personal AI Infrastructure — Compression Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Compression module provides multi-format data compression with gzip, zstd, and parallel compression engines. It includes archive management, streaming compression, and convenient file-level APIs for reducing storage and transfer costs.

## PAI Capabilities

### Compression API

```python
from codomyrmex.compression import compress, decompress, get_compressor

# Compress/decompress data in memory
compressed = compress(data, level=6, format="gzip")
original = decompress(compressed, format="gzip")

# Get a specific compressor engine
compressor = get_compressor("zstd")
```

### File Operations

```python
from codomyrmex.compression import compress_file, decompress_file

# Compress/decompress files on disk
output_path = compress_file("data.json", format="gzip", level=6)
original_path = decompress_file("data.json.gz")
```

### Advanced Engines

```python
from codomyrmex.compression import ZstdCompressor, ParallelCompressor, ArchiveManager

# Zstandard for high-performance compression
zstd = ZstdCompressor(level=3)

# Parallel compression for large datasets
para = ParallelCompressor(workers=4, format="gzip")

# Archive management (tar, zip)
archive = ArchiveManager()
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `compress` | Function | Compress bytes data |
| `decompress` | Function | Decompress bytes data |
| `compress_file` | Function | Compress a file on disk |
| `decompress_file` | Function | Decompress a file on disk |
| `get_compressor` | Function | Get engine by format |
| `ArchiveManager` | Class | Archive creation and extraction |
| `ZstdCompressor` | Class | Zstandard compression engine |
| `ParallelCompressor` | Class | Multi-threaded compression |

## PAI Algorithm Phase Mapping

| Phase | Compression Contribution |
|-------|--------------------------|
| **BUILD** | Compress build artifacts and deployment packages |
| **EXECUTE** | Stream-compress large data transfers |
| **LEARN** | Compress memory snapshots and log archives |

## Architecture Role

**Core Layer** — Consumed by `serialization/`, `containerization/`, `ci_cd_automation/`, and `agentic_memory/` for efficient data storage.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
