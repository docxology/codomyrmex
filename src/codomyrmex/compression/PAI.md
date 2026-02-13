# Personal AI Infrastructure — Compression Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Compression module for Codomyrmex. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.compression import Compressor, ArchiveManager, CompressionError, compress, decompress, get_compressor
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Compressor` | Class | Compressor |
| `ArchiveManager` | Class | Archivemanager |
| `CompressionError` | Class | Compressionerror |
| `ZstdCompressor` | Class | Zstdcompressor |
| `ParallelCompressor` | Class | Parallelcompressor |
| `compress` | Function/Constant | Compress |
| `decompress` | Function/Constant | Decompress |
| `get_compressor` | Function/Constant | Get compressor |
| `compress_data` | Function/Constant | Compress data |
| `decompress_data` | Function/Constant | Decompress data |
| `auto_decompress` | Function/Constant | Auto decompress |
| `compress_file` | Function/Constant | Compress file |
| `decompress_file` | Function/Constant | Decompress file |

## PAI Algorithm Phase Mapping

| Phase | Compression Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
