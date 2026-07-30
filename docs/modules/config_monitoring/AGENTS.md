# Codomyrmex Agents — docs/modules/config_monitoring

## Purpose

Maintain the module documentation signpost for `codomyrmex.config_monitoring`.
The source module and specification remain authoritative for runtime behavior.

## Key Files

- [`README.md`](README.md) — module overview and operating notes.
- [`../../../src/codomyrmex/config_monitoring/`](../../../src/codomyrmex/config_monitoring/) — source of truth.
- [`../../../src/codomyrmex/config_monitoring/SPEC.md`](../../../src/codomyrmex/config_monitoring/SPEC.md) — contract.

## Dependencies

Documentation-only surface. Runtime dependencies are owned by the source
module and project lockfile.

## Development Guidelines

- Preserve relative links and run `make docs-check` after edits.
- Describe watcher lifetime, hashing, and persistence behavior precisely.
- Do not commit local snapshots or environment secrets.

## Navigation

- [Module README](README.md)
- [Module index](../README.md)
