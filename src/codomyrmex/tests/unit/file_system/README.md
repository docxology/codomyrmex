# File System Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `file_system` module. Covers core file operations (create, read, append, delete), directory operations, file finding, duplicate detection, hashing, disk usage, and the FileSystemManager class.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `test_create_and_read_file` | Core file create and read round-trip |
| `test_append_to_file` | File append operations |
| `test_delete_file_and_dir` | File and directory deletion |
| `test_list_dir` | Directory listing |
| `test_find_files` | File finding by pattern |
| `test_find_duplicates` | Duplicate file detection via hashing |
| `test_disk_usage` | Disk usage statistics |
| `TestCreateFile` | File creation with overwrite, unicode, multiline, parent dirs |
| `TestReadFile` | File reading, nonexistent/directory error handling |
| `TestAppendToFile` | Append operations, multiple appends, newline handling |
| `TestDelete` | File/dir deletion, recursive, nonexistent handling |
| `TestCreateDirectory` | Directory creation |

## Test Structure

```
tests/unit/file_system/
    __init__.py
    test_core.py        # Core FileSystemManager operations
    test_file_system.py # Detailed file/directory CRUD operations
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/file_system/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/file_system/ --cov=src/codomyrmex/file_system -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../file_system/README.md)
- [All Tests](../README.md)
