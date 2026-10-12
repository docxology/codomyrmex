# Repository documentation tooling specification

## Purpose

The repository tooling composes read-only audits, portable receipts, source
link rewriting, and explicit maintenance commands around the canonical MkDocs
build.

## Required gates

`make docs-check` and `just docs-check` must remain behaviorally aligned and
run:

1. RASP pair presence in check mode;
2. package-wide README/AGENTS integrity;
3. comprehensive link validation;
4. code references, MCP tool names, and API signatures;
5. content quality and AGENTS structure validation;
6. aggregate quality and triple-check;
7. strict MkDocs.

The composition may write reports under `output/` and build output under
`site/`; it must not rewrite editorial sources.

## Specification validation

`validate_mcp_tool_specs.py` statically discovers MCP registrations and checks
documented tool names within their owning package. It fails on nonexistent
documented tools under `--fail-on-broken`; undocumented tools are informational.

`validate_api_signatures.py` resolves documented callables in their packages
and compares parameter names. Unsupported documented parameters and missing
required parameters fail under `--fail-on-broken`. Defaults, annotations, and
parameter order are outside this comparison. Unresolved signatures and skipped
files must be reported explicitly and do not constitute successful validation.

Both commands support JSON receipts and bounded explicit specification paths.
Neither rewrites specifications. Package imports in the API validator may
require optional dependencies; this gate is not a runtime or scientific
acceptance test.

## README/AGENTS audit

`audit_readme_agents.py` must:

- cover the repository root, RASP first-party roots, and documented test
  directories;
- reuse the RASP exclusion boundary;
- validate pair members, H1 presence, relative Markdown targets, documented
  Python entry points, and local skill paths;
- inventory generic/legacy content separately from blocking errors;
- produce deterministic, repository-relative JSON and Markdown receipts;
- return nonzero under `--strict` only for blocking errors.

## Module enrichment

`enrich_module_docs.py` must:

- require one of `--dry-run` or `--apply`;
- protect curated README/AGENTS files even under force;
- preserve existing unmarked files unless the matching force flag is supplied;
- support bounded repeated `--module` selection;
- generate explicit imports and source-derived descriptions;
- avoid stale hard-coded package versions and dates.

Repository-wide apply is prohibited during the active hand-pass freeze.

## MkDocs hook

`mkdocs_hooks.py` may rewrite links only within the staged build view. It must
resolve supported repository files and directory destinations, canonicalize
README/index conflicts, and leave missing targets visible to strict-mode
failure.

## Testing

Use real temporary repositories. Required negative controls include missing
pairs, broken paths, path traversal, dry-run byte preservation, curated-file
protection, and portable report output.

## Navigation

- [README](README.md)
- [Agent guidance](AGENTS.md)
- [Maintenance guide](../../docs/development/documentation.md)
