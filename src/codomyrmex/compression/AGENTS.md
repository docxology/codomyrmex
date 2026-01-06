# Codomyrmex Agents — src/codomyrmex/compression

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Compression Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Compression module providing data compression utilities and archive handling (zip, tar, gzip, etc.) for the Codomyrmex platform. This module integrates with `documents` and `build_synthesis` modules to handle compressed data and archives.

The compression module serves as the compression layer, providing format-agnostic compression interfaces with support for multiple compression formats and archive types.

## Module Overview

### Key Capabilities
- **Data Compression**: Compress data using various algorithms
- **Data Decompression**: Decompress data from various formats
- **Archive Creation**: Create archives containing multiple files
- **Archive Extraction**: Extract files from archives
- **Streaming**: Support streaming compression/decompression

### Key Features
- Format-agnostic compression interface
- Support for multiple compression formats
- Archive management with multiple files
- Configurable compression levels
- Streaming support for large files

## Function Signatures

### Compression Functions

```python
def compress(data: bytes, level: int = 6) -> bytes
```

Compress data using the configured format.

**Parameters:**
- `data` (bytes): Data to compress
- `level` (int): Compression level (0-9, higher = more compression)

**Returns:** `bytes` - Compressed data

```python
def decompress(data: bytes) -> bytes
```

Decompress data using the configured format.

**Parameters:**
- `data` (bytes): Compressed data

**Returns:** `bytes` - Decompressed data

**Raises:**
- `CompressionError`: If decompression fails

### Archive Functions

```python
def create_archive(files: list[Path], output: Path, format: str = "zip") -> bool
```

Create an archive containing multiple files.

**Parameters:**
- `files` (list[Path]): List of file paths to include
- `output` (Path): Output archive path
- `format` (str): Archive format (zip, tar, etc.)

**Returns:** `bool` - True if successful

```python
def extract_archive(archive: Path, output: Path) -> bool
```

Extract files from an archive.

**Parameters:**
- `archive` (Path): Archive file path
- `output` (Path): Output directory path

**Returns:** `bool` - True if successful

**Raises:**
- `CompressionError`: If extraction fails

### Streaming Functions

```python
def compress_stream(input_stream: IO[bytes], output_stream: IO[bytes], level: int = 6) -> None
```

Compress data from input stream to output stream.

**Parameters:**
- `input_stream` (IO[bytes]): Input stream
- `output_stream` (IO[bytes]): Output stream
- `level` (int): Compression level

```python
def decompress_stream(input_stream: IO[bytes], output_stream: IO[bytes]) -> None
```

Decompress data from input stream to output stream.

**Parameters:**
- `input_stream` (IO[bytes]): Input stream
- `output_stream` (IO[bytes]): Output stream

### Format Detection

```python
def detect_format(data: bytes) -> Optional[str]
```

Detect compression format from data.

**Parameters:**
- `data` (bytes): Compressed data

**Returns:** `Optional[str]` - Format name if detected, None otherwise

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `compressor.py` – Base compressor interface
- `archive_manager.py` – Archive creation and extraction
- `formats/` – Format-specific implementations
  - `zip_handler.py` – ZIP format handler
  - `tar_handler.py` – TAR format handler
  - `gzip_handler.py` – GZIP format handler

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Compression Protocols

All compression operations within the Codomyrmex platform must:

1. **Error Handling** - Handle compression/decompression errors gracefully
2. **Format Validation** - Validate formats before processing
3. **Streaming Support** - Support streaming for large files
4. **Resource Management** - Properly manage file handles and memory
5. **Format Detection** - Auto-detect formats when possible

### Integration Guidelines

When integrating with other modules:

1. **Use Documents Module** - Integrate with document handling
2. **Build Artifacts** - Support build_synthesis for artifact compression
3. **Cache Integration** - Support cache compression for storage efficiency
4. **Error Recovery** - Implement fallback when compression fails

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [documents](../documents/AGENTS.md) - Document handling
    - [build_synthesis](../build_synthesis/AGENTS.md) - Build automation

