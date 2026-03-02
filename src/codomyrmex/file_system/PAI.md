# Personal AI Infrastructure -- File System Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

File system operations module providing managed file reading and directory listing. Exposes `FileSystemManager` for programmatic access and two MCP tools for AI agent integration.

## PAI Capabilities

### File System Operations

```python
from codomyrmex.file_system import FileSystemManager, create_file_system_manager

manager = create_file_system_manager()
content = manager.read_file("src/codomyrmex/cli/core.py")
entries = manager.list_directory("src/codomyrmex/", recursive=True)
```

## MCP Tools (Auto-discovered)

| Tool                        | Description                                      |
|-----------------------------|--------------------------------------------------|
| file_system_read            | Read file contents at a given path               |
| file_system_list_directory  | List directory entries, optionally recursive      |

## PAI Phase Mapping

| Phase   | Tool/Class                   | Usage                                  |
|---------|------------------------------|----------------------------------------|
| OBSERVE | file_system_read             | Read file contents for inspection      |
| OBSERVE | file_system_list_directory   | Discover files and directory structure  |
| EXECUTE | FileSystemManager            | Programmatic file system management    |

## Key Exports

| Export                    | Type     | Description                        |
|---------------------------|----------|------------------------------------|
| FileSystemManager         | Class    | Core file system operations        |
| create_file_system_manager| Function | Factory for FileSystemManager      |

## Integration Notes

- Has `mcp_tools.py` -- auto-discovered via MCP bridge (2 tools).
- Read operations do not require trust elevation.
- Write operations (if added) would require TRUSTED state via `/codomyrmexTrust`.
