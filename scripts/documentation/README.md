# documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation files and guides.

## Local validation

From the repository root, with `output/` present (`mkdir -p output`):

```bash
uv run python scripts/documentation/validate_links_comprehensive.py \
  --repo-root . --output output --format both
# optional: add --fail-on-broken to exit non-zero on broken internal links (CI uses this)

uv run python scripts/documentation/analyze_content_quality.py \
  --repo-root . --output output --format both --min-score 60

uv run python scripts/documentation/validate_agents_structure.py \
  --repo-root . --output output --format both

uv run python scripts/documentation/enforce_quality_gate.py \
  --repo-root . --output output \
  --min-quality-score 70 --max-broken-links 10 --max-placeholders 100 \
  --min-agents-valid-rate 80 --allow-warnings
```

**Placeholders (quality gate):** `enforce_quality_gate.py` sums per-file `metrics.placeholder_count` from `analyze_content_quality.py`. That count reflects actionable markers (task-style `TODO:`, `FIXME:`, HTML comment TODOs, `[TBD]` / `[WIP]`, etc.), not prose like “TODO queues” or `example.com` URLs. See the module docstring in `analyze_content_quality.py` for the exact rules.

## Directory Contents
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `analyze_content_quality.py` – File
- `audit_documentation.py` – File
- `bootstrap_agents_readmes.py` – File
- `deepen_src_docs.py` – File
- `doc_generator.py` – File
- `enforce_quality_gate.py` – File
- `enrich_docs_layer.py` – File
- `enrich_module_docs.py` – File
- `enrich_spec_and_submodules.py` – File
- `enrich_src_docs.py` – File
- `enrich_thin_readmes.py` – File
- `examples/` – Subdirectory
- `fix_docs_readmes.py` – File
- `fix_documentation.py` – File
- `fix_docusaurus_module_links.py` – Rewrites `SPEC.md` / `PAI.md` / `mcp_tools.py` links under `src/codomyrmex/documentation/docs/modules` after module doc sync
- `fix_formatting.py` – File
- `fix_install_sections.py` – File
- `fix_readme_quality.py` – File
- `generate_dashboard.py` – File
- `improve_crossrefs.py` – File
- `orchestrate.py` – File
- `validate_agents_structure.py` – File
- `validate_links_comprehensive.py` – File

## Common commands

Run from repository root (`uv run`):

```bash
# Fail CI-style if any internal markdown link is broken
uv run python scripts/documentation/validate_links_comprehensive.py \
  --repo-root . --output output --format both --fail-on-broken

# Fix Docusaurus module copies that still point at sibling SPEC/PAI/mcp_tools
uv run python scripts/documentation/fix_docusaurus_module_links.py
uv run python scripts/documentation/fix_docusaurus_module_links.py --dry-run
```

## Navigation
- **Parent Directory**: [scripts](../README.md)
- **Project Root**: ../../README.md
