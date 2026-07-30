# security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Automation and utility scripts.

## Directory Contents
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `audit/` – Subdirectory
- `audit_secrets.py` – File
- `audit_uv_lock.py` – Exports and audits the complete `uv.lock` graph
- `compliance/` – Subdirectory
- `examples/` – Subdirectory
- `orchestrate.py` – File
- `scan_dependencies.py` – File
- `scanning/` – Subdirectory
- `secrets/` – Subdirectory

## Navigation
- **Parent Directory**: [scripts](../README.md)
- **Project Root**: ../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)

## Locked dependency audit

From the repository root:

```bash
make audit-lock
```

The command audits all dependency groups and extras from `uv.lock`, not the
environment containing the audit tool. It applies one version-gated exception:
`PYSEC-2026-151` is ignored only for `wasmtime==42.0.0`, which the upstream
RustSec record marks unaffected.
