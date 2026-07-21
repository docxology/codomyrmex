# Codomyrmex Root Specification


**Version**: v0.1.0 | **Status**: Active | **Last Updated**: May 2026

## Purpose
This specification formally defines the expected behavior, interfaces, and architecture for the `Codomyrmex Root` module.

## Architectural Constraints
- **Modularity**: Components must maintain strict modular boundaries.
- **Real Execution**: The design guarantees executable paths without reliance on stubbed or mocked data.
- **Data Integrity**: All input and output signatures must be strictly validated.

## Workflow semantics

- `command` steps run with the local shell and are trusted-workflow-only. Do
  not execute unreviewed workflow files or workflow content from untrusted
  users.
- A non-zero exit status, timeout, or execution error is terminal by default;
  later steps are not run.
- Unimplemented step types are terminal by default and use their existing
  status value (`script_not_implemented` or `unimplemented`).
- `continue_on_error: true` explicitly preserves the prior continue behavior
  for a step whose failure is expected and safe to ignore.
- The result schema remains stable: each executed step has a `name` and
  `status`, with command output and timing fields when available.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../README.md)
