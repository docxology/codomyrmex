# Compression -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Format Support
- gzip, zlib, ZIP, and Zstandard compression formats.
- Configurable compression levels (1-9 for gzip/zlib).

### FR-2: Operations
- In-memory compress/decompress for bytes data.
- File-level compress_file/decompress_file for disk operations.
- Auto-detection of compression format via `auto_decompress`.

### FR-3: Advanced
- ParallelCompressor for multi-threaded compression of large datasets.
- ArchiveManager for ZIP archive creation, extraction, and listing.

## Interface Contracts

```python
def compress(data: bytes, level: int = 6, format: str = "gzip") -> bytes
def decompress(data: bytes, format: str | None = None) -> bytes
def compress_file(input_path: str, output_path: str | None = None,
                  format: str = "gzip", level: int = 6) -> str
def decompress_file(input_path: str, output_path: str | None = None,
                    format: str = "gzip") -> str
```

## Navigation

- **Source**: [src/codomyrmex/compression/](../../../../src/codomyrmex/compression/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
