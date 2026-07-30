<!-- readme: curated -->

# Documentation package

`codomyrmex.documentation` provides documentation analysis, generation,
maintenance, MCP, and website-building components. Repository-wide editorial
policy and the canonical MkDocs build live outside this package under `docs/`
and `scripts/documentation/`.

## Public boundary

Use public exports from `codomyrmex.documentation` and documented submodules.
Do not treat the legacy Docusaurus source or its generated `.docusaurus/` tree
as the canonical Codomyrmex documentation site.

Key surfaces:

| Path | Role |
| :--- | :--- |
| `pai.py` | Documentation PAI metadata and module-doc helpers |
| `mcp_tools.py` | MCP-exposed documentation operations |
| `maintenance.py` | Package maintenance operations |
| `quality/` | Documentation quality models and checks |
| `education/` | Documentation education helpers |
| `scripts/` | Package-native scanners and generators |
| `docs/`, `src/`, `static/` | Legacy Docusaurus source and assets |
| `API_SPECIFICATION.md` | Public Python interface |
| `MCP_TOOL_SPECIFICATION.md` | MCP schemas and behavior |
| `SPEC.md` | Normative package design |
| `SECURITY.md` | Input, path, and generation safety |

## Validation

From the repository root:

```bash
uv run --locked pytest -q tests/unit/documentation tests/integration/documentation
uv run --locked ruff check src/codomyrmex/documentation tests/unit/documentation
uv run --locked ty check --output-format concise src/codomyrmex/documentation
make docs-check
```

The package tests use real files and temporary directories; broad repository
rewrites are not test fixtures.

## Generation boundary

Package-native scripts include historical broad repair tools. Their presence
does not make them safe to run over a dirty checkout. Follow
[`scripts/AGENTS.md`](scripts/AGENTS.md), inspect current CLI behavior, and use
dry-run or check modes before any approved mutation.

The package-wide README/AGENTS hand-pass freeze prohibits broad apply runs.
Curated files must be preserved.

## Navigation

- [Agent instructions](AGENTS.md)
- [Functional specification](SPEC.md)
- [API specification](API_SPECIFICATION.md)
- [MCP tool specification](MCP_TOOL_SPECIFICATION.md)
- [Package script guidance](scripts/AGENTS.md)
- [Repository documentation guide](../../../docs/development/documentation.md)
- [Parent package](../README.md)
- [Repository root](../../../README.md)
