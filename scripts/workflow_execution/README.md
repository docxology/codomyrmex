# workflow_execution

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Runs declarative workflows whose command steps execute through the local shell.
Shell execution is intentionally trusted-workflow-only: workflow files must be
reviewed and treated as executable code before they are run.

Execution stops after a command returns a non-zero status, raises an error, or
times out. Unimplemented step types are terminal as well. A step may set
`continue_on_error: true` when continuing is an explicit part of the trusted
workflow contract. Results retain the existing schema and report the terminal
status without attempting later steps by default.

Example:

```json
{"name": "checks", "steps": [{"name": "lint", "command": "ruff check .", "timeout": 60}]}
```

## Directory Contents
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `workflow_runner.py` – File

## Navigation
- **Parent Directory**: [scripts](../README.md)
- **Project Root**: ../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
