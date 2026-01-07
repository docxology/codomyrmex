# compression

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Data compression utilities and archive handling. Provides format-agnostic compression interface with support for gzip, zlib, zip, tar, and tar.gz formats, with streaming support, configurable compression levels, and automatic format detection.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `archive_manager.py` – File
- `compressor.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.compression import Compressor, ArchiveManager, compress, decompress
from pathlib import Path

# Basic compression/decompression
compressor = Compressor(format="gzip")
data = b"Data to compress"
compressed = compressor.compress(data, level=9)
decompressed = compressor.decompress(compressed)

# Format detection
format = compressor.detect_format(compressed)

# Archive management
archive_manager = ArchiveManager()
files = [Path("file1.txt"), Path("file2.txt")]
archive_manager.create_archive(files, Path("archive.zip"), format="zip")
archive_manager.extract_archive(Path("archive.zip"), Path("output_dir"))
```

