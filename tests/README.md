<!-- readme: curated -->

# Test suite

The repository test tree covers package units, integration boundaries,
language adapters, orchestration, scripts, and performance behavior. Detailed
zero-mock and marker rules are in [SPEC.md](SPEC.md) and
[RUNNING_TESTS.md](RUNNING_TESTS.md).

## Run

```bash
# Focused diagnostic run; no package coverage claim
uv run --locked pytest -q tests/unit/<module>

# Full configured coverage gate
make test
```

Plain `uv run pytest` skips the coverage threshold for speed. `make test`
measures the configured source scope and enforces the 60% floor.

## Test classes

- `unit/`: deterministic package and script behavior
- `integration/`: real cross-component boundaries
- `performance/`: explicit benchmark and load checks
- `languages/`: language tooling behavior
- `orchestrator/`: workflow and fractal orchestration
- `fixtures/`: versioned non-secret test inputs
- `scripts/`: repository-script regression tests

Optional services and platform capabilities should be detected and skipped with
a clear reason when unavailable. Tests must not fabricate external success.

## Navigation

- [Agent guidance](AGENTS.md)
- [Testing specification](SPEC.md)
- [Running tests](RUNNING_TESTS.md)
- [Unit tests](unit/README.md)
- [Integration tests](integration/README.md)
- [Repository root](../README.md)
