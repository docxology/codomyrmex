# ide/vscode

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Integration with Visual Studio Code. Provides programmatic access to the Extension API, workspace management, settings manipulation, and debugging capabilities through a workspace-aware client.

## Key Exports

- **`VSCodeClient`** -- Client extending `IDEClient` for Visual Studio Code integration. Key capabilities:

  **Connection**
  - `connect()` -- Detect a VS Code workspace by checking for `.vscode/` directory, `*.code-workspace` files, or workspace path existence
  - `disconnect()` -- Clean up connection state
  - `is_connected()` -- Check connection status
  - `get_capabilities()` -- Return supported features (commands, workspace, extensions, debug, tasks, terminal, source_control) and available command IDs

  **Extensions**
  - `list_extensions()` -- List installed extensions with name, publisher, version, and enabled status

  **Commands**
  - `execute_command()` -- Execute a VS Code command by command ID
  - `list_commands()` -- List available command IDs (save, saveAll, formatDocument, terminal.new, debug.start, debug.stop)

  **Settings**
  - `get_settings()` -- Read workspace settings from `.vscode/settings.json`
  - `update_settings()` -- Merge and write workspace settings; creates `.vscode/` directory if needed

  **Debugging**
  - `start_debug()` -- Start a debug session with optional configuration
  - `stop_debug()` -- Stop the current debug session

  **File Operations**
  - `get_active_file()` / `open_file()` / `get_open_files()` -- IDE file management

## Directory Contents

- `__init__.py` - VSCodeClient with settings, extensions, debug, and command management (261 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [ide](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
