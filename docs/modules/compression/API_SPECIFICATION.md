# compression - API Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The compression module provides data compression and archive management utilities supporting multiple formats including gzip, zlib, and zip.

## Classes

### Compressor

Main compression utility class supporting multiple formats.

```python
from codomyrmex.compression import Compressor
```

#### Constructor

```python
Compressor(format: str = "gzip")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | `str` | `"gzip"` | Compression format: `"gzip"`, `"zlib"`, or `"zip"` |

#### Methods

##### compress

```python
def compress(data: bytes, level: int = 6) -> bytes
```

Compress data using the configured format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `bytes` | - | Data to compress |
| `level` | `int` | `6` | Compression level (0-9, higher = more compression) |

**Returns**: `bytes` - Compressed data

**Raises**: `CompressionError` if compression fails

##### decompress

```python
def decompress(data: bytes) -> bytes
```

Decompress data using the configured format.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `bytes` | Compressed data |

**Returns**: `bytes` - Decompressed data

**Raises**: `CompressionError` if decompression fails

##### compress_stream

```python
def compress_stream(input_stream: IO[bytes], output_stream: IO[bytes], level: int = 6) -> None
```

Compress data from input stream to output stream.

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_stream` | `IO[bytes]` | Input stream |
| `output_stream` | `IO[bytes]` | Output stream |
| `level` | `int` | Compression level |

##### decompress_stream

```python
def decompress_stream(input_stream: IO[bytes], output_stream: IO[bytes]) -> None
```

Decompress data from input stream to output stream.

##### detect_format

```python
def detect_format(data: bytes) -> Optional[str]
```

Detect compression format from data magic bytes.

**Returns**: Format name (`"gzip"`, `"zlib"`, `"zip"`) or `None` if unknown

---

### ArchiveManager

Archive creation and extraction utility.

```python
from codomyrmex.compression import ArchiveManager
```

#### Methods

##### create_archive

```python
def create_archive(files: list[Path], output_path: Path, format: str = "zip") -> bool
```

Create an archive from files.

##### extract_archive

```python
def extract_archive(archive_path: Path, output_dir: Path) -> bool
```

Extract archive to directory.

---

## Exceptions

### CompressionError

```python
from codomyrmex.compression import CompressionError
```

Raised when compression or decompression operations fail. Inherits from `CodomyrmexError`.

---

## Usage Examples

### Basic Compression

```python
from codomyrmex.compression import Compressor

# Create gzip compressor
compressor = Compressor("gzip")

# Compress data
data = b"Hello, World!" * 100
compressed = compressor.compress(data, level=9)

# Decompress
decompressed = compressor.decompress(compressed)
assert decompressed == data
```

### Format Detection

```python
from codomyrmex.compression import Compressor

compressor = Compressor()
format_name = compressor.detect_format(compressed_data)
print(f"Detected format: {format_name}")
```

### Stream Compression

```python
from io import BytesIO
from codomyrmex.compression import Compressor

compressor = Compressor("zlib")

input_buffer = BytesIO(b"Large data to compress...")
output_buffer = BytesIO()

compressor.compress_stream(input_buffer, output_buffer)
compressed = output_buffer.getvalue()
```

---

## Integration

### Dependencies
- Python standard library (`gzip`, `zlib`, `zipfile`)
- `codomyrmex.logging_monitoring` for logging
- `codomyrmex.exceptions` for error handling

### Related Modules
- [`documents`](../documents/API_SPECIFICATION.md) - Document compression
- [`deployment`](../deployment/API_SPECIFICATION.md) - Build artifact compression
- [`cache`](../cache/API_SPECIFICATION.md) - Cache compression

---

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../AGENTS.md)
