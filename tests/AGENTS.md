<!-- agents: curated -->

# Agent guidance for tests

## Operating contract

- Follow the repository zero-mock policy. Use real classes, files, subprocesses,
  temporary directories, and local services.
- Narrow environment, cwd, and temporary-path isolation is permitted as
  described in [SPEC.md](SPEC.md).
- Test public behavior and failure receipts, not implementation trivia.
- Add negative controls for path traversal, tampering, absent evidence,
  no-mode execution, dry-run byte preservation, and optional dependencies when
  relevant.
- Never write to real user configuration, credentials, home directories,
  external services, or publication targets.
- Keep tests deterministic under the fixed-epoch or seeded contracts used by
  the owning module.
- Do not weaken or delete a failing test merely to make a gate green; establish
  whether implementation, expectation, or environment is wrong.
- Update the nearest README/SPEC when test scope or invocation changes.

## Validation

Run the narrowest relevant test first:

```bash
uv run --locked pytest -q tests/unit/<module>
```

Then run formatting, lint, typing, and the full coverage gate appropriate to the
change. `make test` is the authoritative 60% coverage invocation.

## Navigation

- [Human overview](README.md)
- [Testing specification](SPEC.md)
- [Running tests](RUNNING_TESTS.md)
- [Repository agent contract](../AGENTS.md)
