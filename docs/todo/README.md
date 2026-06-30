# docs/todo

> Per-module scope documents tracking outstanding implementation work, open design questions, and phase-by-phase acceptance criteria.

## Overview

Each file in this directory is a scope document for one Codomyrmex module. Scope documents are more detailed than a task list: they describe the executive summary of the module's purpose, break work into phases with explicit acceptance criteria, and record the current implementation status per subsystem.

This directory is distinct from the root `TO-DO.md`, which holds repo-wide, cross-cutting backlog rows. When a `TO-DO.md` row references a specific module, the detailed spec and acceptance criteria live here.

## Contents

| File | Module | Status |
|------|--------|--------|
| `COLONY_KERNEL.md` | Colony Kernel (control plane, 8 MCP tools, 9 subsystems) | Fully implemented — all 4 phases complete, 457 tests |

## File Naming Convention

Files are named `MODULE_NAME.md` in `SCREAMING_SNAKE_CASE`, matching the directory name of the module under `src/codomyrmex/`.

## Usage

When starting work on a new module:

1. Create `docs/todo/MODULE_NAME.md` with the executive summary, phase plan, and acceptance criteria.
2. Link it from the module's `docs/modules/<name>/SPEC.md` under a `## Outstanding Work` section.
3. As phases complete, update the status table in this file and annotate the scope document.
4. When all phases are done, add `## Status: Complete` at the top of the scope document.

## Related

- **Root backlog**: [../../TO-DO.md](../../TO-DO.md)
- **Module docs**: [../modules/](../modules/)
- **Agent coordination**: [AGENTS.md](AGENTS.md)
