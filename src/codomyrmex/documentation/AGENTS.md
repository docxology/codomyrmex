<!-- agents: curated -->

# Agent guidance for `codomyrmex.documentation`

## Purpose

This package owns reusable documentation functionality. It does not own the
repository's editorial source hierarchy or replace the canonical MkDocs gate.

## Development Guidelines

- Preserve public exports, MCP schemas, PAI behavior, and documentation
  specifications together.
- Use centralized logging for package operations.
- Keep path handling repository-relative or caller-supplied; never embed
  absolute home paths or credentials in generated artifacts.
- Default audits to read-only behavior and make mutation explicit.
- Exclude submodules, vendor trees, caches, and generated output unless a
  caller deliberately opts into a documented scope.
- Preserve curated README/AGENTS markers under every generation or repair path.
- Use real temporary files in tests; do not mock filesystem or subprocess
  behavior.
- Do not run broad package-native generators during the active hand-pass
  freeze.

## Key Files

- [README.md](README.md) — package overview and build boundary
- [SPEC.md](SPEC.md) — normative package behavior
- [API_SPECIFICATION.md](API_SPECIFICATION.md) — public Python exports
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) — MCP schemas
- `mcp_tools.py` — implemented MCP handlers
- `quality/` and `scripts/` — analysis and maintenance subpackages

## Interface changes

Before changing a function, class, or method, run GitNexus impact analysis.
When a public or MCP interface changes, update:

- `API_SPECIFICATION.md`;
- `MCP_TOOL_SPECIFICATION.md` when applicable;
- `PAI.md`;
- `SPEC.md` and `SECURITY.md` for changed contracts;
- relevant README/AGENTS guidance and tests;
- package and root changelogs.

## Validation

```bash
uv run --locked pytest -q tests/unit/documentation tests/integration/documentation
uv run --locked ruff check src/codomyrmex/documentation tests/unit/documentation
uv run --locked ty check --output-format concise src/codomyrmex/documentation
make docs-check
```

The strict site build may depend on an up-to-date generated manuscript HTML
artifact. Validate manuscript inputs separately with `make manuscript-check`.

## Navigation

- [Package overview](README.md)
- [Package scripts](scripts/AGENTS.md)
- [Functional specification](SPEC.md)
- [Security](SECURITY.md)
- [Repository documentation guide](../../../docs/development/documentation.md)
- [Parent package](../AGENTS.md)
- [Repository agent contract](../../../AGENTS.md)
