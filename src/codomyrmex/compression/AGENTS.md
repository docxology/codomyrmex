# Codomyrmex Agents — src/codomyrmex/compression

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Data compression utilities and archive handling. Provides format-agnostic compression interface with support for gzip, zlib, zip, tar, and tar.gz formats, with streaming support and automatic format detection.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `archive_manager.py` – Archive creation and extraction manager
- `compressor.py` – Compression/decompression implementation

## Key Classes and Functions

### Compressor (`compressor.py`)
- `Compressor(format: str = "gzip")` – Initialize compressor with specified format (gzip, zlib, zip)
- `compress(data: bytes, level: int = 6) -> bytes` – Compress data using the configured format (level 0-9)
- `decompress(data: bytes) -> bytes` – Decompress data using the configured format
- `compress_stream(input_stream: IO[bytes], output_stream: IO[bytes], level: int = 6) -> None` – Compress data from input stream to output stream
- `decompress_stream(input_stream: IO[bytes], output_stream: IO[bytes]) -> None` – Decompress data from input stream to output stream
- `detect_format(data: bytes) -> Optional[str]` – Detect compression format from data (checks magic bytes)

### ArchiveManager (`archive_manager.py`)
- `ArchiveManager()` – Manager for archive operations
- `create_archive(files: list[Path], output: Path, format: str = "zip") -> bool` – Create an archive containing multiple files (zip, tar, tar.gz)
- `extract_archive(archive: Path, output: Path) -> bool` – Extract files from an archive

### Module Functions (`__init__.py`)
- `compress(data: bytes, level: int = 6, format: str = "gzip") -> bytes` – Compress data
- `decompress(data: bytes, format: Optional[str] = None) -> bytes` – Decompress data
- `get_compressor(format: str = "gzip") -> Compressor` – Get a compressor instance

### Exceptions
- `CompressionError` – Raised when compression operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation