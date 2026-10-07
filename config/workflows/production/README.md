# production

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

## Overview

Workflow definitions loaded by default: a `WorkflowManager` created in the
repository root (including `codomyrmex workflow list` / `run`) loads every
`*.json` here, and `codomyrmex workflow create` writes new definitions to
`config/workflows/production/` under the current directory. See
[../README.md](../README.md) for the format.

## Directory Contents

- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `test_workflow.json` – smoke test: `environment_setup.validate_environment`

## Navigation

- **Parent Directory**: [workflows](../README.md)
- **Project Root**: ../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Maintenance Notes

- Keep this document synchronized with adjacent source files.
- Update sibling README, AGENTS, and SPEC documents together.
- Preserve working examples when changing public behavior.
- Prefer measured validation output over inferred status claims.
- Record any remaining gaps in TODO.md or the nearest planning document.
