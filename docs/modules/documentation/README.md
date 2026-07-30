<!-- readme: curated -->

# Documentation module

The documentation module provides package audits, consistency and quality
heuristics, PAI generation, MCP tools, legacy maintenance helpers, and a
package-local Docusaurus lifecycle. The repository's authoritative reader build
is strict MkDocs through `make docs-check`.

## Start here

- [API specification](API_SPECIFICATION.md)
- [MCP tool specification](MCP_TOOL_SPECIFICATION.md)
- [Functional specification](SPEC.md)
- [Usage examples](USAGE_EXAMPLES.md)
- [Security](SECURITY.md)
- [PAI mapping](PAI.md)
- [Source package](../../../src/codomyrmex/documentation/)

## Validation

```bash
uv run --locked pytest -q tests/unit/documentation tests/integration/documentation
make docs-check
```

## Boundary

Package quality scores and RASP presence are diagnostic evidence, not proof
that documentation is semantically accurate. Local site builds and hashes do
not establish publication, DOI assignment, accessibility conformance, or
external actuation.

## Navigation

- [Agent guidance](AGENTS.md)
- [Module index](../README.md)
- [Repository documentation guide](../../development/documentation.md)
- [Repository root](../../../README.md)
