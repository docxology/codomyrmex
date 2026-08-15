# Documentation maintenance

Codomyrmex documentation is maintained as a source-linked package surface, not
as an independent prose tree. Commands, interfaces, counts, and publication
claims must be verified against current source or generated receipts.

## Source ownership

| Surface | Owner and purpose |
| :--- | :--- |
| `README.md`, `AGENTS.md`, `SPEC.md` | Repository entry points and governing contracts |
| `docs/` | Canonical reader-facing guides and MkDocs sources |
| `src/codomyrmex/<module>/` | Module-local API, MCP, PAI, security, and usage documentation |
| `docs/modules/<module>/` | Reader-oriented mirrors; refresh only through the reviewed module-doc workflow |
| `scripts/documentation/` | Repository maintenance, auditing, and MkDocs hooks |
| `src/codomyrmex/documentation/` | Distributable documentation package and legacy Docusaurus assets |
| `output/` and `site/` | Generated receipts and builds; never edit as source |
| Git submodules | Upstream-owned worktrees with their own instructions and history |

Raw manuscript sections under `docs/manuscript/` are Pandoc sources.
They are excluded from direct MkDocs rendering. The publication pipeline
produces the semantic HTML report consumed by the documentation build.

## Authoritative validation

Run the locked package target from the repository root:

```bash
make docs-check
```

It performs, in order:

1. scoped RASP README/AGENTS pair checking;
2. package-wide README/AGENTS command, skill, and relative-link auditing;
3. comprehensive repository link validation;
4. content-quality and agent-structure validation;
5. the documentation quality gate and triple-check;
6. a strict MkDocs build.

The equivalent `just docs-check` recipe is kept in parity. Validation may write
receipts beneath `output/` and the MkDocs build beneath `site/`; it does not
rewrite editorial source files.

Run the manuscript integrity check separately when manuscript inputs or
publication artifacts change:

```bash
make manuscript-check
```

After rendering a release candidate, require the stronger source-current and
PDF/UA-2 gate as well:

```bash
make manuscript-pdf-check
```

This strict target requires the rendered HTML, tagged content/distribution PDFs,
qpdf/pdfinfo/veraPDF receipts, current source/configuration hashes, and a
source-current release bundle. It is intentionally separate from the lighter
input/provenance check because generated publication artifacts are not checked
into the source tree.

## README and AGENTS contracts

The RASP pair check governs live directories under `src/codomyrmex/`, `docs/`,
`projects/`, `scripts/`, `config/`, and `.github/`. The broader auditor adds the
repository root and documented test directories, while respecting the same
submodule, vendor, cache, and generated-tree exclusions.

```bash
# Read-only presence check; nonzero when a governed directory has a gap
uv run --locked python scripts/rasp_gap_report.py --repo-root . --check

# Generate the durable gap report intentionally
uv run --locked python scripts/rasp_gap_report.py --repo-root .

# Validate pairs, headings, local links, documented Python paths, and skills
uv run --locked python scripts/documentation/audit_readme_agents.py \
  --repo-root . --strict
```

The last command writes portable JSON and Markdown receipts to
`output/readme_agents_audit.{json,md}`. Legacy version labels, generic leaf
copy, and duplicated generated punctuation are inventoried separately from
blocking integrity errors. A generic phrase can be unhelpful without being
factually wrong; review those files in bounded hand-pass batches.

README and AGENTS files have distinct roles:

- `README.md` explains what a directory contains, who uses it, and how to run
  or navigate it.
- `AGENTS.md` defines scope, ownership, constraints, validation, and safe
  mutation boundaries for automated contributors.
- `SPEC.md` records normative behavior where that directory owns a functional
  contract.

Do not duplicate long inventories in both README and AGENTS. Prefer links to an
authoritative specification or generated inventory.

## Hand-pass freeze and generation safety

A repository-wide README/AGENTS hand pass is active. Do not run broad bootstrap,
enrichment, placeholder-repair, or missing-file generators in apply mode while
the tree is frozen.

Protection markers must appear near the beginning of a reviewed file:

```html
<!-- readme: curated -->
<!-- agents: curated -->
```

Preview module mirror changes one module at a time:

```bash
uv run --locked python scripts/documentation/enrich_module_docs.py \
  --repo-root . --dry-run --module <module>
```

Applying is deliberately explicit:

```bash
uv run --locked python scripts/documentation/enrich_module_docs.py \
  --repo-root . --apply --module <module>
```

Existing unmarked files are preserved unless the matching
`--force-readmes`, `--force-agents`, or `--force-specs` flag is supplied.
Curated README/AGENTS files remain protected under force. Review the dry-run
diff and current Git status before applying.

The broad bootstrap also supports `--dry-run`, but its output is discovery
evidence during the freeze:

```bash
uv run --locked python \
  -m codomyrmex.documentation.scripts.bootstrap_agents_readmes \
  --repo-root . --dry-run
```

The placeholder checker is likewise fail-closed:

```bash
uv run --locked python \
  -m codomyrmex.documentation.scripts.placeholder_check \
  --repo-root . --dry-run
```

Use `--apply` only after the freeze is lifted and the complete proposed path
set has been reviewed. It skips configured submodules by default.

## Counts and evidence

Volatile counts must come from shared producers:

```bash
uv run --locked python scripts/doc_inventory.py
uv run --locked python scripts/doc_inventory.py --pytest
uv run --locked python scripts/src_structure_audit.py --json
```

Record current definitions and results in
[`docs/reference/inventory.md`](../reference/inventory.md). Do not copy old MCP
tool, test, workflow, module, bibliography, or figure totals into unrelated
glossaries and citation files.

For technical-report claims, distinguish:

- formal properties established by code structure or proof;
- deterministic fixtures and contract tests;
- observed empirical measurements;
- hypotheses and roadmap work;
- external or best-effort validation boundaries.

Local ledger integrity is not evidence that an external action occurred or was
safe. Publication, DOI assignment, deployment, and independent accessibility
conformance remain separate status layers.

## Links and commands

- Use relative Markdown links for repository files.
- Link to the actual source file when a local mirror does not contain the
  target.
- Link directories to a real `README.md` or index surface when the destination
  is ambiguous.
- Write repository-root commands unless a different working directory is
  stated immediately before the command.
- Use `uv run --locked` and the appropriate dependency group for reproducible
  contributor commands.
- Never document a Python file, shell script, skill, or console command without
  confirming that it exists in the current checkout.
- Do not put absolute home paths, tokens, or credentials in examples or
  generated receipts.

The MkDocs hook in `scripts/documentation/mkdocs_hooks.py` rewrites valid
repository-file links outside `docs/`, canonicalizes supported directory links,
and resolves README/index collisions. Missing targets remain unresolved so
strict mode fails.

## Examples

Examples should use public, explicit imports and real signatures:

```python
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)
logger.info("documentation example")
```

Avoid wildcard imports, invented result shapes, placeholder secrets, and APIs
that exist only in prose. Test executable examples when practical; otherwise
label them as illustrative and keep them outside copy-paste command blocks.

## Mermaid diagrams

Use fenced `mermaid` blocks with theme-neutral syntax:

- avoid hard-coded `style`, `classDef`, and theme colors;
- use `subgraph graph_id [Human-readable label]`;
- quote labels containing punctuation;
- avoid reserved identifiers such as `end` and `graph`;
- connect edges to real nodes, not renderer-dependent subgraph identifiers.

Repository maintenance helpers:

```bash
uv run --locked python scripts/strip_mermaid_style_lines.py
uv run --locked python scripts/normalize_mermaid_subgraphs.py
```

Review their diffs before retaining changes.

## Review checklist

- The reader-facing purpose and working directory are clear.
- Commands and code examples execute against current source.
- README, AGENTS, SPEC, API, MCP, PAI, security, tests, and changelog surfaces
  agree where the change affects them.
- Counts are generated and dated, not independently hard-coded.
- Internal links, headings, anchors, and directory destinations resolve.
- Figures have captions, concise alternatives, long descriptions when needed,
  evidence classes, and redundant encodings.
- Claims preserve negative results, limitations, and external validation
  boundaries.
- Generated output was refreshed in producer order and is not being mistaken
  for editable source.
- `make docs-check` and relevant manuscript/package tests pass.

## Navigation

- [Developer documentation index](README.md)
- [Testing strategy](testing-strategy.md)
- [Inventory](../reference/inventory.md)
- [README/AGENTS hand-pass tracker](../plans/readme_agents_hand_pass.md)
- [Repository agent contract](../../AGENTS.md)
