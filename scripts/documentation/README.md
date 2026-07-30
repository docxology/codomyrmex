<!-- readme: curated -->

# Repository documentation tooling

This directory contains the repository-level audits, MkDocs integration, and
reviewed maintenance commands used by `make docs-check`. It is separate from
the distributable `codomyrmex.documentation` package.

## Authoritative validation

From the repository root:

```bash
make docs-check
```

For focused diagnosis:

```bash
uv run --locked --group docs python scripts/rasp_gap_report.py \
  --repo-root . --check
uv run --locked --group docs python scripts/documentation/audit_readme_agents.py \
  --repo-root . --strict
uv run --locked --group docs python scripts/documentation/validate_links_comprehensive.py \
  --repo-root . --format both --fail-on-broken
uv run --locked --group docs python scripts/documentation/validate_agents_structure.py \
  --repo-root . --format both --fail-on-invalid
```

The README/AGENTS auditor writes
`output/readme_agents_audit.{json,md}`. Other validators document their receipt
paths in `--help` and command output. The aggregate quality gate consumes the
JSON receipts produced by the preceding validators, so the canonical
composition emits both human-readable Markdown and machine-readable JSON.

## Tool groups

| Tool | Role | Mutation boundary |
| :--- | :--- | :--- |
| `audit_readme_agents.py` | Pair, heading, command, skill, and local-link integrity | Reports only |
| `validate_links_comprehensive.py` | Repository Markdown links | Reports only |
| `analyze_content_quality.py` | Content-quality metrics | Reports only |
| `validate_agents_structure.py` | AGENTS structure and required sections | Reports only |
| `enforce_quality_gate.py` | Aggregated documentation policy | Reports only |
| `mkdocs_hooks.py` | Repository-file and directory-link rewriting for MkDocs | Build-time transformation |
| `enrich_module_docs.py` | Source-derived `docs/modules/<name>/` mirrors | Explicit `--apply`; curated files protected |
| `bootstrap_agents_readmes.py` | Wrapper for broad leaf-doc bootstrap | Preview first; frozen during hand pass |
| `fix_docusaurus_module_links.py` | Legacy Docusaurus mirror link repair | Supports `--dry-run`; review before apply |

Other scripts in this directory are maintenance utilities, not implied release
gates. Inspect their `--help`, source, Git impact, and proposed path set before
running them.

## Safe module-doc workflow

The module enricher is fail-closed:

```bash
# Preview one module
uv run --locked python scripts/documentation/enrich_module_docs.py \
  --repo-root . --dry-run --module <module>

# Apply reviewed changes to one module
uv run --locked python scripts/documentation/enrich_module_docs.py \
  --repo-root . --apply --module <module>
```

Existing unmarked files require an explicit per-file-type force flag.
`<!-- readme: curated -->` and `<!-- agents: curated -->` files are never
overwritten by the enricher.

## Hand-pass freeze

The package-wide README/AGENTS hand pass is active. Do not run broad bootstrap,
enrichment, or repair commands in apply mode. Use read-only audit output for
discovery and make bounded, reviewed edits. See the
[hand-pass tracker](../../docs/plans/readme_agents_hand_pass.md).

## Placeholder repair

The package-native placeholder checker also requires an explicit mode:

```bash
uv run --locked python \
  -m codomyrmex.documentation.scripts.placeholder_check \
  --repo-root . --dry-run
```

`--apply` is intentionally omitted here while the freeze is active. The
producer now consumes optional terminal punctuation so a future approved repair
does not generate doubled periods.

## Navigation

- [Agent instructions](AGENTS.md)
- [Documentation maintenance guide](../../docs/development/documentation.md)
- [Parent scripts](../README.md)
- [Repository root](../../README.md)
