# File System - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `file_system` module provides a unified interface for filesystem operations including CRUD, directory management, searching, and metadata retrieval.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `FileSystemManager` | Unified API for file/directory CRUD, search, and metadata operations |

### 2.2 Factory Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `create_file_system_manager` | `(**kwargs) -> FileSystemManager` | Create a configured FileSystemManager instance |

## 3. Usage Example

```python
from codomyrmex.file_system import create_file_system_manager

fs = create_file_system_manager()
contents = fs.read_file("/path/to/file.txt")
fs.write_file("/path/to/output.txt", contents)
files = fs.search("*.py", recursive=True)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
