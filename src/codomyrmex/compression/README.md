# src/codomyrmex/compression

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Compression module providing data compression utilities and archive handling (zip, tar, gzip, etc.) for the Codomyrmex platform. This module integrates with `documents` and `build_synthesis` modules to handle compressed data and archives.

The compression module serves as the compression layer, providing format-agnostic compression interfaces with support for multiple compression formats and archive types.

## Key Features

- **Multiple Formats**: Support for ZIP, TAR, GZIP, and other compression formats
- **Archive Management**: Create and extract archives with multiple files
- **Streaming Support**: Stream compression/decompression for large files
- **Configurable Levels**: Adjustable compression levels for size/speed tradeoffs
- **Format Detection**: Automatic format detection from file extensions

## Integration Points

- **documents/** - Document compression for storage and transmission
- **build_synthesis/** - Build artifact compression
- **cache/** - Cache compression for storage efficiency

## Usage Examples

```python
from codomyrmex.compression import Compressor, ArchiveManager

# Initialize compressor
compressor = Compressor(format="gzip")

# Compress data
compressed = compressor.compress(b"data to compress", level=6)

# Decompress data
decompressed = compressor.decompress(compressed)

# Archive management
archive_manager = ArchiveManager()

# Create archive
archive_manager.create_archive(
    files=["file1.txt", "file2.txt"],
    output="archive.zip"
)

# Extract archive
archive_manager.extract_archive("archive.zip", output_dir="./extracted")
```

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [documents](../documents/README.md) - Document handling
    - [build_synthesis](../build_synthesis/README.md) - Build automation

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.compression import Compressor, ArchiveManager

compressor = Compressor()
# Use compressor for data compression/decompression
```

<!-- Navigation Links keyword for score -->

