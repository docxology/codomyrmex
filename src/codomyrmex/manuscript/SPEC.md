# Manuscript Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Functional Requirements

- Compute manuscript token variables from real repository state (test
  counts, coverage, module counts, file hashes) rather than hardcoded values.
- Inject computed variables into the manuscript build via
  `inject_manuscript_variables()`.
- Generate one figure per `fig_*()` generator under `figures/`, sharing
  palettes, config loading, and provenance helpers from `figures/_common.py`.
- Resolve a distinct caption, concise alternative, and extended description for every
  configured figure and retain those strings in the generated figure registry.
- Preserve categorical meaning through direct labels, position, shape, line style, or
  another non-colour channel, with the shared palette meeting the tested contrast floor.
- Run all figure generators through `figures.orchestrator.main()`.
- Keep `scripts/generate_manuscript_figures.py` as the supported command-line entry
  point; its implementation delegates to the package registry.

## Non-Functional Requirements

- Deterministic given fixed repository state; no network calls.
- Tests use real filesystem and subprocess execution; no mocks.
- Generated HTML associates every figure with its extended description; the appendix
  exposes the same descriptions as searchable text for static/PDF readers.

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
