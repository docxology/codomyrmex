# File System -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The file_system module provides a unified interface for filesystem operations available to AI agents. It wraps file CRUD, directory management, glob-based search, content hashing (SHA-256 by default), duplicate detection, and disk usage analysis behind the `FileSystemManager` class. Two MCP tools (`file_system_read`, `file_system_list_directory`) expose read-only filesystem access through the PAI MCP bridge for safe agent consumption.

## Key Files

| File | Class/Function | Role |
|------|----------------|------|
| `__init__.py` | Exports `FileSystemManager`, `create_file_system_manager` | Module entry point |
| `core.py` | `FileSystemManager` | Central class: `create_file()`, `read_file()`, `append_to_file()`, `delete()`, `create_directory()`, `list_dir()`, `get_info()`, `find_files()`, `get_hash()`, `find_duplicates()`, `get_disk_usage()` |
| `core.py` | `create_file_system_manager()` | Convenience factory function |
| `mcp_tools.py` | `file_system_read` | MCP tool: reads a file and returns contents with metadata |
| `mcp_tools.py` | `file_system_list_directory` | MCP tool: lists directory entries with optional recursion |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `file_system_read` | Read a file and return its contents, path, and size_bytes. Returns `{"status": "error", ...}` on failure. | SAFE |
| `file_system_list_directory` | List entries in a directory. Accepts `path` (default: ".") and `recursive` (default: false). Returns entry list and count. | SAFE |

Both MCP tools are read-only and do not modify the filesystem. They instantiate a fresh `FileSystemManager()` internally on each call.

## Agent Instructions

1. **Use MCP tools for read-only access** -- Prefer `file_system_read` and `file_system_list_directory` when operating through the PAI MCP bridge. These are SAFE-level tools that do not require trust elevation.
2. **Use `FileSystemManager` for write operations** -- Import `FileSystemManager` directly for `create_file()`, `append_to_file()`, `delete()`, `create_directory()`. These are destructive operations and should be gated behind trust verification in PAI contexts.
3. **Always use `pathlib.Path`** -- The module uses `pathlib.Path` internally for all path operations. String paths are automatically converted, but prefer passing `Path` objects.
4. **Handle `FileExistsError`** -- `create_file()` raises `FileExistsError` when `overwrite=False` and the file already exists. Default is `overwrite=True`.
5. **Handle `FileNotFoundError`** -- `read_file()` raises `FileNotFoundError` for missing files. `get_info()` also raises `FileNotFoundError`.
6. **Delete with caution** -- `delete(path, recursive=True)` uses `shutil.rmtree()` for directories. Without `recursive=True`, `rmdir()` only works on empty directories.
7. **Use `find_files()` for glob searching** -- Supports any glob pattern (e.g., `"*.py"`, `"**/*.json"`). Searches recursively via `rglob()`.
8. **Use `get_hash()` for integrity checks** -- Defaults to SHA-256. Supports any algorithm from `hashlib` (e.g., `"md5"`, `"sha512"`).
9. **Use `find_duplicates()` for deduplication** -- Returns a dict mapping content hashes to lists of `Path` objects. Only entries with 2+ files are included.

## Operating Contracts

- `create_file()` auto-creates parent directories via `mkdir(parents=True, exist_ok=True)`. It writes content as UTF-8.
- `read_file()` reads as UTF-8. Raises `FileNotFoundError` if the path is not a file (including for directories).
- `delete()` returns `False` if the path does not exist (logs warning, does not raise). Returns `True` on successful deletion.
- `list_dir()` returns `Path` objects. With `recursive=True`, uses `rglob("*")`. With `recursive=False`, uses `iterdir()`.
- `get_info()` returns a dict with keys: `name`, `path` (absolute), `size`, `is_dir`, `extension`, `created_at`, `modified_at`, `permissions`.
- `get_hash()` raises `ValueError` for non-file paths. Reads in 4096-byte chunks for memory efficiency.
- `find_duplicates()` silently skips files that cannot be hashed (logs error, continues). Only returns hashes with 2+ matching files.
- `get_disk_usage()` falls back to `"."` if the resolved path does not exist.
- All significant mutations (creates, deletes) are logged via `logging_monitoring`.
- **Zero-Mock Policy**: Tests must use `pytest`'s `tmp_path` fixture for real filesystem operations. No `unittest.mock` for filesystem calls.
- **No silent fallbacks**: Missing files raise explicit exceptions rather than returning default values.

## Common Patterns

```python
from codomyrmex.file_system import FileSystemManager

fs = FileSystemManager()

# Create and read a file
fs.create_file("/tmp/test.txt", content="Hello, world!")
content = fs.read_file("/tmp/test.txt")
assert content == "Hello, world!"

# Get file metadata
info = fs.get_info("/tmp/test.txt")
print(f"Size: {info['size']} bytes, Modified: {info['modified_at']}")

# Find files by pattern
python_files = fs.find_files("*.py", search_path="/path/to/project")
print(f"Found {len(python_files)} Python files")

# Check for duplicates
dupes = fs.find_duplicates("/path/to/project")
for hash_val, paths in dupes.items():
    print(f"Duplicate ({hash_val[:8]}): {[str(p) for p in paths]}")

# Disk usage
usage = fs.get_disk_usage("/")
print(f"Disk: {usage['percent']:.1f}% used ({usage['used'] / 1e9:.1f} GB)")
```

```python
# MCP tool usage (via PAI bridge)
# These return dicts with "status" key
result = file_system_read(path="/etc/hostname")
if result["status"] == "success":
    print(result["content"])

listing = file_system_list_directory(path="/tmp", recursive=False)
print(f"Entries: {listing['count']}")
```

## Testing Patterns

```python
from codomyrmex.file_system import FileSystemManager

class TestFileSystemManager:
    def test_create_and_read(self, tmp_path):
        fs = FileSystemManager()
        file_path = tmp_path / "test.txt"
        fs.create_file(file_path, content="hello")
        assert fs.read_file(file_path) == "hello"

    def test_delete_file(self, tmp_path):
        fs = FileSystemManager()
        file_path = tmp_path / "deleteme.txt"
        file_path.write_text("temp")
        assert fs.delete(file_path) is True
        assert not file_path.exists()

    def test_get_hash_sha256(self, tmp_path):
        fs = FileSystemManager()
        file_path = tmp_path / "hash_test.txt"
        file_path.write_text("content")
        h = fs.get_hash(file_path)
        assert len(h) == 64  # SHA-256 hex digest length

    def test_read_missing_file_raises(self):
        fs = FileSystemManager()
        import pytest
        with pytest.raises(FileNotFoundError):
            fs.read_file("/nonexistent/file.txt")
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `file_system_read`, `file_system_list_directory` + direct `FileSystemManager` | TRUSTED for writes |
| **Architect** | Read-only | `file_system_read`, `file_system_list_directory` | SAFE |
| **QATester** | Validation | `file_system_read`, `file_system_list_directory` | SAFE |
| **Researcher** | Read-only | `file_system_read`, `file_system_list_directory` | SAFE |

### Engineer Agent
**Use Cases**: Creating files during BUILD, cleaning up temp artifacts during EXECUTE, computing file hashes for integrity verification, detecting duplicate files for deduplication workflows.

### Architect Agent
**Use Cases**: Listing directory structures during OBSERVE to understand project layout, reading config files for architectural review.

### QATester Agent
**Use Cases**: Reading test output files, listing test directories, verifying file creation during integration tests.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
