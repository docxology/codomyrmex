<!-- readme: curated -->

# Repository scripts

This tree contains repository maintenance, validation, release, manuscript,
agent, security, and module-specific commands. A script is not safe to run
merely because it is versioned: inspect its CLI defaults, write scope,
submodule exclusions, and tests first.

## Authoritative entry points

| Command or path | Role |
| :--- | :--- |
| `doc_inventory.py` | Shared volatile package/documentation counts |
| `src_structure_audit.py` | Runtime module docs/API/MCP/test parity |
| `rasp_gap_report.py` | Scoped README/AGENTS pair receipt and read-only check |
| `documentation/` | Documentation gates, MkDocs hook, and reviewed maintenance |
| `validate_manuscript_integrity.py` | Manuscript citations, cross-references, claims, figures, and artifacts |
| `compile_manuscript.py` | Technical-report rendering and bookend inputs |
| `release/` and `codomyrmex.release` | Release validation and publication bundle workflow |
| `security/` | Locked dependency and security audit helpers |
| `audits/` | Source, export, RASP, and policy audits |
| `review/` | Diff review and SARIF utilities |
| `agents/` | Agent-specific launch and maintenance commands |
| `sair/` | Separate SAIR submodule worktree |

## Common validation

Run from the repository root:

```bash
uv run --locked python scripts/doc_inventory.py
uv run --locked python scripts/src_structure_audit.py --json
uv run --locked python scripts/rasp_gap_report.py --repo-root . --check
make docs-check
make manuscript-check
make manuscript-pdf-check
```

`manuscript-check` validates the source-bound inputs and evidence without
requiring generated publication outputs. `manuscript-pdf-check` is the strict
release-candidate gate: it requires source-current HTML, both tagged PDF/UA-2
artifacts, qpdf/pdfinfo/veraPDF receipts, and the matching release bundle.

Use each script's `--help` only after confirming that help parsing is
side-effect free. Maintained mutators should require explicit dry-run or apply
modes.

## Mutation boundary

- Preserve the dirty worktree and inspect the complete target path set.
- Never run broad documentation generation during the active hand-pass freeze.
- Do not rewrite Git submodules, vendored code, caches, or generated build
  trees as part of a package-wide pass.
- Avoid no-argument “fix all” or “run all” scripts unless their implementation,
  tests, and current scope have been reviewed.
- Keep output receipts portable and free of credentials and absolute home
  paths.

## Navigation

- [Agent guidance](AGENTS.md)
- [Documentation tooling](documentation/README.md)
- [Documentation maintenance guide](../docs/development/documentation.md)
- [Repository root](../README.md)
