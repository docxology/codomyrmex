# Personal AI Infrastructure — Ide Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

IDE Integration Module. This is an **Application Layer** module.

## PAI Capabilities

```python
from codomyrmex.ide import IDEClient, IDEStatus, IDECommand
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `IDEClient` | Class | Ideclient |
| `IDEStatus` | Class | Idestatus |
| `IDECommand` | Class | Idecommand |
| `IDECommandResult` | Class | Idecommandresult |
| `FileInfo` | Class | Fileinfo |
| `IDEError` | Class | Ideerror |
| `ConnectionError` | Class | Connectionerror |
| `CommandExecutionError` | Class | Commandexecutionerror |
| `SessionError` | Class | Sessionerror |
| `ArtifactError` | Class | Artifacterror |
| `CursorClient` | Class | Cursorclient |

## PAI Algorithm Phase Mapping

| Phase | Ide Contribution |
|-------|------------------------------|
| **OBSERVE** | Data gathering and state inspection |
| **EXECUTE** | Execution and deployment |

## Architecture Role

**Application Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
