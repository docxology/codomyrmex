# AGENTS.md — docs/todo

> Technical reference for AI agents and contributors working in this directory.

## Purpose

`docs/todo/` holds per-module scope documents that track outstanding implementation work, outstanding tests, and open design questions for each Codomyrmex module.

## Key Files

| File | Purpose |
|------|---------|
| `COLONY_KERNEL.md` | Scope document for the Colony Kernel module: 4-phase implementation plan, subsystem API sketches, invariants, and implementation status table |

## Conventions

- One `.md` file per module, named `MODULE_NAME.md` in `SCREAMING_SNAKE_CASE`.
- Each file is a **scope document**, not a flat task list. It includes: executive summary, implementation phases, acceptance criteria per phase, and current status.
- Status fields use the values: `Planned`, `In Progress`, `Implemented`, `Blocked`.
- When a module's scope document is fully implemented and its items are closed, move completed acceptance criteria to the module's `SPEC.md` and archive the scope document with a `## Status: Complete` header.
- Do not duplicate content already in `TO-DO.md` at the project root. `docs/todo/` files are module-scoped; `TO-DO.md` tracks cross-cutting backlog rows.

## Relationship to TO-DO.md

`TO-DO.md` at the project root contains repo-wide, cross-cutting backlog rows. Module scope documents here contain per-module phase plans and detailed acceptance criteria. If a row in `TO-DO.md` references a module, the detailed spec lives in the corresponding file here.

## Navigation

- **Project root backlog**: [../../TO-DO.md](../../TO-DO.md)
- **Module docs**: [../modules/](../modules/)
- **Source**: [../../src/codomyrmex/](../../src/codomyrmex/)
