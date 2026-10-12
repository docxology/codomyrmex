# security

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: August 2026

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

The command exports every dependency group and extra from `uv.lock`, retains
all distinct package/version pins across environment markers, and audits
markerless batches without resolving or installing those requirements. Each
batch contains only one version of a package. Missing or malformed advisory
reports fail the gate.

Two existing exceptions are bound to exact reported versions:

- `PYSEC-2026-151` for `wasmtime==42.0.0`: the recorded upstream applicability
  review concerns Rust crate 43.0.0, with earlier versions unaffected
  ([upstream advisory](https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-hfr4-7c6c-48w2)).
- `PYSEC-2026-3740` for `nltk==3.10.3`: the existing review records an unpatched
  transitive dependency of the optional Safety audit tool; Codomyrmex does not
  import NLTK. Its model persistence exposure remains an explicit exception
  ([upstream advisory](https://github.com/nltk/nltk/security/advisories/GHSA-8mgp-746c-j5xp)).

Exceptions never extend to another package version. JSON output retains them
in `ignored_vulns` with their justification; zero unexcepted findings does not
mean zero advisory records or certify these prior applicability reviews anew.
