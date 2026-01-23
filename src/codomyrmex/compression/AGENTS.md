# Codomyrmex Agents — src/codomyrmex/compression

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Compression module provides data compression and decompression utilities supporting multiple formats including gzip, zlib, and ZIP. It offers configurable compression levels, stream-based compression, automatic format detection via magic bytes, file compression utilities, and archive creation/extraction capabilities.

## Active Components

### Core Infrastructure

- `compressor.py` - Main compression/decompression operations
  - Key Classes: `Compressor`, `CompressionError`
  - Key Functions: `compress()`, `decompress()`, `compress_stream()`, `decompress_stream()`, `detect_format()`
- `archive_manager.py` - Archive creation and extraction
  - Key Classes: `ArchiveManager`
  - Key Functions: `create_archive()`, `extract_archive()`
- `zstd_compressor.py` - Zstandard compression support
  - Key Classes: `ZstdCompressor`
- `parallel.py` - Parallel compression operations
  - Key Classes: `ParallelCompressor`

### Utility Functions

- `compress_data()` - Module-level compression convenience function
- `decompress_data()` - Module-level decompression convenience function
- `auto_decompress()` - Automatic format detection and decompression
- `compress_file()` - File compression utility
- `decompress_file()` - File decompression utility
- `compare_formats()` - Compare compression ratios across formats

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `Compressor` | compressor | Multi-format compression (gzip, zlib, zip) |
| `ArchiveManager` | archive_manager | ZIP and tar archive operations |
| `ZstdCompressor` | zstd_compressor | Zstandard compression support |
| `ParallelCompressor` | parallel | Multi-threaded compression |
| `CompressionError` | compressor | Exception for compression failures |
| `compress()` | __init__ | Compress data with specified format |
| `decompress()` | __init__ | Decompress data with specified format |
| `compress_data()` | compressor | Convenience function for compression |
| `decompress_data()` | compressor | Convenience function for decompression |
| `auto_decompress()` | compressor | Auto-detect format and decompress |
| `compress_file()` | compressor | Compress files to disk |
| `decompress_file()` | compressor | Decompress files from disk |
| `detect_format()` | compressor | Detect compression format via magic bytes |
| `get_compression_ratio()` | compressor | Calculate compression ratio |
| `compare_formats()` | compressor | Benchmark compression across formats |
| `create_archive()` | archive_manager | Create ZIP/tar archives |
| `extract_archive()` | archive_manager | Extract archive contents |

## Operating Contracts

1. **Logging**: All operations use `logging_monitoring` for structured logging
2. **Error Handling**: Operations raise `CompressionError` for consistent error handling
3. **Format Support**: Supports gzip, zlib, ZIP, tar, and tar.gz formats
4. **Compression Levels**: Configurable levels 0-9 (higher = more compression)
5. **Auto-Detection**: Magic byte detection for gzip (0x1f8b), ZIP (PK), zlib (0x78xx)

## Integration Points

- **logging_monitoring** - Structured logging for all operations
- **exceptions** - Base exception classes (`CodomyrmexError`)
- **encryption** - Compressed data can be encrypted for secure storage

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| encryption | [../encryption/AGENTS.md](../encryption/AGENTS.md) | Cryptographic operations |
| cache | [../cache/AGENTS.md](../cache/AGENTS.md) | Caching with compression support |
| documents | [../documents/AGENTS.md](../documents/AGENTS.md) | Document handling |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
