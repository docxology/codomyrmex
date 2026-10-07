# Google Workspace

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

**Module**: `codomyrmex.agents.google_workspace` | **Category**: Specialized | **Last Updated**: March 2026

## Overview

Integration with Google Workspace APIs — Docs, Sheets, Drive, Calendar — through the `gws` (Google Workspace CLI) binary. `GoogleWorkspaceRunner` wraps `gws <service> <resource> <method>` calls as subprocesses for programmatic use.

## Key Classes

| Class | Purpose |
| :--- | :--- |
| `GoogleWorkspaceRunner` | Runs `gws` commands (`run`, `schema`, `check`) and returns their output |
| `GWSConfig` / `get_config` | Configuration read from environment variables |
| `GWSError` and subclasses | `GWSNotInstalledError`, `GWSTimeoutError`, `GWSAuthError`, `GWSCommandError` |

## Configuration

**Required**: the `gws` binary on `PATH` (`npm install -g @googleworkspace/cli`) and either `GOOGLE_WORKSPACE_CLI_TOKEN` or `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`. Optional: `GOOGLE_WORKSPACE_CLI_ACCOUNT`, `GWS_TIMEOUT`, `GWS_PAGE_ALL`.

## Usage

```python
from codomyrmex.agents.google_workspace import GoogleWorkspaceRunner

runner = GoogleWorkspaceRunner()
print(runner.check())  # gws version, or "" when gws is not installed
result = runner.run("drive", "files", "list", params={"pageSize": 5})
print(result["returncode"], result["stdout"])
```

## Source Module

Source: [`src/codomyrmex/agents/google_workspace/`](../../../src/codomyrmex/agents/google_workspace/)

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/google_workspace/](../../../src/codomyrmex/agents/google_workspace/)
- **Project Root**: [README.md](../../../README.md)

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
- **Spec**: `SPEC.md` is inherited from the nearest parent scope.
