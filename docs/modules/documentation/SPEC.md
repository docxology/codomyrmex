# Documentation module functional specification

The normative specification is maintained with the source package:
[source SPEC](../../../src/codomyrmex/documentation/SPEC.md).

## Reader contract

- Public exports match
  [`codomyrmex.documentation.__all__`](../../../src/codomyrmex/documentation/__init__.py).
- Package quality checks remain labeled as heuristic.
- `audit_rasp()` returns an exit code, not a missing-file count.
- MCP module identifiers reject traversal-shaped input.
- MCP PAI generation defaults to dry-run and reports its proposed hash.
- Repository release documentation is validated by strict MkDocs, not the
  package-local Docusaurus helper alone.
- Broad mutators remain explicit and prohibited during the active hand-pass
  freeze.

## Acceptance

```bash
uv run --locked pytest -q tests/unit/documentation tests/integration/documentation
make docs-check
```

## Navigation

- [README](README.md)
- [API specification](API_SPECIFICATION.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [Source specification](../../../src/codomyrmex/documentation/SPEC.md)
