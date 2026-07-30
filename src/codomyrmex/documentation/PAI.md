# Personal AI Infrastructure — documentation

The documentation module supports the PAI observe, build, and verify phases.
Its generators are local filesystem operations; they do not establish
publication, accessibility conformance, or external release status.

## Observe

```python
from pathlib import Path

from codomyrmex.documentation import (
    DocumentationConsistencyChecker,
    audit_rasp,
    generate_quality_report,
)

exit_code = audit_rasp(Path("src/codomyrmex/documentation"))
quality_markdown = generate_quality_report(Path("."))
consistency = DocumentationConsistencyChecker().check_directory("docs")
```

`audit_rasp()` returns `0` or `1`; it does not return a report object or a count.

## Build

```python
from pathlib import Path

from codomyrmex.documentation import generate_pai_md, update_pai_docs

module_dir = Path("src/codomyrmex/documentation")
preview = generate_pai_md("documentation", module_dir)

# Preview updates to stub PAI files; no writes by default.
update_pai_docs(Path("src/codomyrmex"), apply=False)
```

`write_pai_md()` and `update_pai_docs(..., apply=True)` mutate source files and
require an intentional reviewed call.

## Verify

The authoritative repository gate is external to this package:

```bash
make docs-check
make manuscript-check
```

The first command validates README/AGENTS pairs, commands, links, content,
structure, triple-check, and strict MkDocs. The second validates technical
report evidence and generated publication relationships.

## MCP tools

| Tool | Default behavior | Mutation boundary |
| :--- | :--- | :--- |
| `codomyrmex.generate_module_docs` | Generates and hashes a proposed `PAI.md` with `dry_run=true` | `dry_run=false` replaces one validated module's PAI file |
| `codomyrmex.audit_rasp_compliance` | Read-only RASP presence check | No source writes |

The generation name is retained for compatibility; its implemented scope is
PAI-only. See [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md).

## Phase mapping

| PAI phase | Contribution |
| :--- | :--- |
| OBSERVE | Read documentation structure, quality, and consistency |
| BUILD | Produce source-derived PAI content and package-local site artifacts |
| VERIFY | Check RASP presence, links, structure, and quality |
| LEARN | Persist reviewed receipts and changelog evidence outside runtime state |

## Boundaries

- Heuristic quality scores are not proof of technical accuracy.
- RASP presence is not proof that prose is current.
- A clean MkDocs build is not a DOI assignment or publication event.
- `qpdf --check` is structural, not PDF/UA conformance.
- Local ledgers and hashes do not independently observe external actuation.

## Navigation

- [Package overview](README.md)
- [API specification](API_SPECIFICATION.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [Repository PAI bridge](../../../PAI.md)
