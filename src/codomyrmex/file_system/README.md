# File System Module README.md

## Overview
The `file_system` module in Codomyrmex provides a simple and consistent interface for common filesystem operations. It wraps standard library functions from `os`, `shutil`, and `pathlib` into a more coherent and safe API for the Codomyrmex ecosystem.

## Features
- **Directory Operations**: List, create, delete, and walk directories.
- **File CRUD**: Read, write, append, delete, move, and copy files.
- **Metadata**: Get detailed file/directory information, size, and timestamps.
- **Advanced Tools**: Find duplicate files, search by pattern, and analyze disk usage.

## Usage Example
```python
from pathlib import Path
from codomyrmex.file_system.core import FileSystemManager

fs = FileSystemManager()
path = Path("example.txt")

# Create a file
fs.create_file(path, "Hello, Codomyrmex!")

# Get file info
info = fs.get_info(path)
print(f"File size: {info['size']} bytes")

# Read content
content = fs.read_file(path)
print(f"Content: {content}")

# Delete file
fs.delete(path)
```

## Integration
- **Logging**: All file operations are logged via `codomyrmex.logging_monitoring`.
- **Validation**: Path validation and safety checks are performed before operations.

## Testing
Unit tests for this module are located in `src/codomyrmex/tests/unit/file_system/` and follow a strict zero-mock policy.
