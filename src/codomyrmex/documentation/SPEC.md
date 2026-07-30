# Documentation package functional specification

## Purpose

`codomyrmex.documentation` provides reusable documentation quality analysis,
RASP auditing, PAI generation, legacy root-maintenance helpers, and a
package-local Docusaurus lifecycle. Repository editorial policy and the
canonical strict MkDocs build remain external package concerns.

## Functional requirements

1. Public exports in `__all__` must match
   [API_SPECIFICATION.md](API_SPECIFICATION.md).
2. Quality and consistency checks must report their scope and avoid source
   mutation.
3. Report paths and findings must be deterministic and portable where a
   durable receipt is produced.
4. PAI generation must derive content from current package exports and
   documentation.
5. Preview modes must not alter target bytes.
6. Mutating maintenance, aggregation, dependency-installation, and site
   lifecycle operations must be called explicitly.
7. MCP module names must resolve to one top-level package beneath
   `src/codomyrmex`; traversal-shaped names must be rejected.
8. MCP PAI generation must default to dry-run and disclose `executed`,
   `dry_run`, target path, and the proposed content hash.
9. RASP audit results must distinguish an exit code from a count of missing
   files.
10. Curated README/AGENTS files and submodule worktrees must remain outside
    unreviewed broad rewrite paths.

## RASP scope

The package-native legacy RASP audit checks Python package directories for:

- `README.md`;
- `AGENTS.md`;
- `SPEC.md`;
- `PAI.md`.

This is not the same contract as the repository-level
`scripts/rasp_gap_report.py` and `audit_readme_agents.py` checks. The repository
tools use explicit first-party roots and exclusions and are authoritative for
the documentation release gate.

## Interface groups

- `quality.audit`: RASP and package completeness
- `quality.quality_assessment`: heuristic 0–100 content scores
- `quality.consistency_checker`: line and structure findings
- `pai`: source-derived PAI generation
- `documentation_website`: package-local Docusaurus lifecycle and aggregation
- `maintenance`: broad legacy source maintenance
- `mcp_tools`: dry-run PAI generation and read-only RASP compliance

## Site boundary

`documentation_website.py` remains a supported package-local Docusaurus
surface. Codomyrmex documentation publication uses the root MkDocs
configuration and `make docs-check`. A successful package-local Docusaurus
build does not satisfy the repository documentation gate.

## Error and security behavior

- Missing or unreadable inputs must be represented in returns, reports, logs,
  or nonzero exit status.
- A caught exception must not be reported as successful execution.
- Paths returned through MCP must be repository-relative.
- Credentials and absolute home paths must not enter generated receipts.
- `dry_run=True` must be byte preserving.
- Network, browser, package-manager, and broad-write operations require
  caller awareness and appropriate authority.

## Acceptance

```bash
uv run --locked pytest -q tests/unit/documentation tests/integration/documentation
uv run --locked ruff check src/codomyrmex/documentation tests/unit/documentation
uv run --locked ty check --output-format concise src/codomyrmex/documentation
make docs-check
```

## Navigation

- [README](README.md)
- [API specification](API_SPECIFICATION.md)
- [MCP tools](MCP_TOOL_SPECIFICATION.md)
- [PAI integration](PAI.md)
- [Security](SECURITY.md)
