# Colony Kernel unit tests

This directory verifies the local Colony Kernel decision and evidence ledger.
The tests distinguish the ordinary caller-reported MCP path from optional or
required kernel modes that locally bind proposals, verdicts, authorization,
execution receipts, and outcomes. They do not claim that the ledger
independently observes external actuation or establishes deployment safety.

## Run

From the repository root:

```bash
uv run --locked pytest tests/unit/colony_kernel -q
```

The package-wide coverage gate is exercised separately by `make test`.

## Scope

- proposal evaluation, policy verdicts, and authorization
- hash-linked ledger integrity and tamper detection
- required versus optional kernel behavior
- execution-receipt and outcome binding
- public API and deterministic fixture contracts

See [AGENTS.md](AGENTS.md) for maintenance constraints and the
[source specification](../../../src/codomyrmex/colony_kernel/SPEC.md) for the
normative behavior.
