# Manuscript Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Functional Requirements

- Compute manuscript token variables from real repository state (test
  counts, coverage, module counts, file hashes) rather than hardcoded values.
- Inject computed variables into the manuscript build via
  `inject_via_infrastructure()`.
- Generate one figure per `fig_*()` generator under `figures/`, sharing
  palettes, config loading, and provenance helpers from `figures/_common.py`.
- Run all figure generators through `figures.orchestrator.main()`.
- Preserve backward-compatible import paths: `src/manuscript_variables.py`
  and `scripts/generate_manuscript_figures.py` remain thin shims.

## Non-Functional Requirements

- Deterministic given fixed repository state; no network calls.
- Tests use real filesystem and subprocess execution; no mocks.

## Validation

```bash
uv run pytest tests/unit/manuscript/ -q
uv run ruff check src/codomyrmex/manuscript
uv run ty check --output-format concise src/codomyrmex/manuscript
```

## Navigation

- **README**: [README.md](README.md)
- **Agent Guidance**: [AGENTS.md](AGENTS.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
