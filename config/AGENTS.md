<!-- agents: curated -->

# Agent guidance for configuration

## Purpose

Define safe maintenance rules for versioned configuration examples and
defaults.

## Development Guidelines

- Never add credentials, tokens, private keys, personal contact data, or
  production-only endpoints.
- Preserve documented precedence between defaults, files, environment
  variables, and explicit caller values.
- Keep examples minimal and syntactically valid.
- Use the owning module's schema and loader rather than inventing a global
  validation rule.
- Reject unsafe values by default when configuration controls authentication,
  host verification, publication, deployment, or destructive operations.
- Update source defaults, example files, tests, README/SPEC/PAI/security, and
  changelog together.
- Run GitNexus impact analysis before changing loader or validator symbols.
- Do not bulk-regenerate folder documentation during the hand-pass freeze.

## Key Files

- [README.md](README.md) — human-facing configuration boundary
- [SPEC.md](SPEC.md) — configuration-surface specification
- `default.yaml` — repository default example
- `hermes_skills_profile.example.yaml` — optional Hermes profile example

## Validation

Run the owning module's focused tests and the repository configuration/source
gates relevant to the change. At minimum:

```bash
uv run --locked ruff check config src/codomyrmex/config_management
uv run --locked pytest -q tests/unit/config_management
```

If a named test path differs, discover the current path with `rg --files tests`
instead of copying a stale command.

## Navigation

- [Human overview](README.md)
- [Configuration specification](SPEC.md)
- [Repository agent contract](../AGENTS.md)
- [Configuration management source](../src/codomyrmex/config_management/)
