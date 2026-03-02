# Personal AI Infrastructure — IDE Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The IDE module provides client interfaces for controlling and automating integrated development environments. It supports multiple IDE backends (Cursor, Antigravity) with a unified abstract interface for file operations, command execution, and editor state management.

## PAI Capabilities

### IDE Client Interface

```python
from codomyrmex.ide import IDEClient, IDEStatus, IDECommand, IDECommandResult

# Abstract IDE client with implementations for different editors
class MyIDEClient(IDEClient):
    def execute(self, command: IDECommand) -> IDECommandResult:
        ...
```

### Cursor IDE Integration

```python
from codomyrmex.ide.cursor import CursorClient

client = CursorClient()
# Open files, navigate to symbols, execute editor commands
# Integrate with Cursor's AI features
```

### IDE Data Models

```python
from codomyrmex.ide import IDEStatus, IDECommand, IDECommandResult, FileInfo

# IDEStatus: CONNECTED, DISCONNECTED, BUSY
# IDECommand: structured editor command
# FileInfo: file metadata for editor context
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `IDEClient` | Abstract Class | Unified IDE interface |
| `CursorClient` | Class | Cursor IDE implementation |
| `IDEStatus` | Enum | IDE connection state |
| `IDECommand` | Dataclass | Structured editor command |
| `IDECommandResult` | Dataclass | Command execution result |
| `FileInfo` | Dataclass | File metadata for editors |

## PAI Algorithm Phase Mapping

| Phase | IDE Contribution |
|-------|-------------------|
| **OBSERVE** | Read editor state (open files, cursor position, active document) |
| **BUILD** | Open and edit files through IDE interface |
| **EXECUTE** | Execute editor commands, apply code changes |
| **VERIFY** | Check IDE diagnostics and linting results |

## Architecture Role

**Interface Layer** — Top-level user interaction module. Consumes `coding/` (code operations) and `git_operations/` (VCS integration). No MCP tools — operates through direct IDE protocol.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.ide import ...`
- CLI: `codomyrmex ide <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
