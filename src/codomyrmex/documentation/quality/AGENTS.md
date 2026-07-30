<!-- agents: curated -->

# Agent guidance for documentation quality

## Purpose

Maintain truthful, deterministic package documentation audit and scoring
behavior.

## Development Guidelines

- Keep heuristic scores labeled as heuristics; never translate them into proof
  of technical accuracy or release readiness.
- Preserve `audit_rasp()` return semantics: `0` for compliant, `1` for gaps.
- Count missing files separately when a consumer needs a count.
- Keep analysis read-only except for an explicitly supplied report path.
- Make paths and finding order deterministic.
- Use real temporary packages and files in tests.
- Update the parent API, MCP, PAI, SPEC, and changelog surfaces when output
  fields or semantics change.

## Key Files

- [README.md](README.md) — reader overview and examples
- [SPEC.md](SPEC.md) — quality contracts and limitations
- `audit.py` — RASP discovery and reports
- `consistency_checker.py` — line and structure findings
- `quality_assessment.py` — heuristic scoring

## Validation

```bash
uv run --locked pytest -q \
  tests/unit/documentation/test_rasp_audit.py \
  tests/unit/documentation/test_quality_comprehensive.py
uv run --locked ruff check src/codomyrmex/documentation/quality
```

## Navigation

- [Human overview](README.md)
- [Functional specification](SPEC.md)
- [Parent agent guidance](../AGENTS.md)
- [Repository agent contract](../../../../AGENTS.md)
