# Documentation coverage assessment

This page records current, reproducible documentation evidence. It does not
retain undated quality scores or historical file counts as if they were live.

## Current README/AGENTS receipt

Measured July 29, 2026 with
`scripts/documentation/audit_readme_agents.py`:

| Measure | Result |
| :--- | ---: |
| Governed directories | 1,550 |
| README files | 1,550 |
| AGENTS files | 1,550 |
| Blocking errors | 0 |
| Generated-punctuation warnings | 916 |
| Generic-boilerplate inventory matches | 2,006 |
| Legacy `v0.1.0` labels | 2,625 |
| Thin files under 15 lines | 25 |

The narrower six-root RASP check reports zero missing README/AGENTS pairs.
Metrics overlap and inventory warnings are not automatically release-blocking.

Receipts:

- `output/readme_agents_audit.json`
- `output/readme_agents_audit.md`
- [`docs/plans/agents-readme-gap-report.md`](../../plans/agents-readme-gap-report.md)

## Reproduce

```bash
uv run --locked python scripts/rasp_gap_report.py --repo-root . --check
uv run --locked python scripts/documentation/audit_readme_agents.py \
  --repo-root . --strict
make docs-check
```

`make docs-check` additionally validates links, content, AGENTS structure,
triple-check, and strict MkDocs. Consult its current command output rather than
copying an old pass status into this page.

## Interpretation

- Pair completeness does not prove content accuracy.
- Heuristic quality scores do not prove code examples execute.
- A strict site build does not prove PDF/UA conformance or publication.
- Known punctuation and generic-copy debt is retired through bounded hand-pass
  batches because a broad rewrite would overwrite concurrent work.

## Navigation

- [Module overview](README.md)
- [Hand-pass tracker](../../plans/readme_agents_hand_pass.md)
- [Inventory](../../reference/inventory.md)
