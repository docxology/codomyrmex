# falsification.checks — AGENTS.md

## Purpose

Per-vector check modules for `FalsificationWorker`. See parent [../AGENTS.md](../AGENTS.md).

## Key Files

- One module per `AttackVector` member (e.g. `check_no_rollback.py`).

## Dependencies

Depends on `..models` for `AttackVector` and `FalsificationReport`.

## Development Guidelines

- Each check module implements exactly one attack vector; keep checks under ~110 LOC (per `worker.py`'s split rationale).
