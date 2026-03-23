# Codomyrmex Agents — scripts/review

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Advisory tooling for local pull-request review and SARIF handling: diff heuristics, Python structural checks, merged Markdown reports, Bandit JSON→SARIF, and SARIF merge/dedupe. Not a substitute for CI or human review.

## Components

| Module | Role |
|:---|:---|
| `pr_analyzer.py` | `git diff` heuristics, risk band, complexity score |
| `code_quality_checker.py` | AST-based Python size/complexity signals |
| `review_report_generator.py` | Optional JSON + SARIF → Markdown/text verdict |
| `sarif_merge.py` | Merge multiple SARIF 2.1.0 files with dedupe |
| `bandit_json_to_sarif.py` | Bandit `-f json` → SARIF (CI helper) |
| `sarif_utils.py` | Shared JSON helpers for this package |
| [README.md](README.md) | Flags, examples, `uv run python scripts/review/...` usage |

## Operating contracts

- Run from repository root so package-relative imports resolve.
- Keep behavior documented in [README.md](README.md) and [docs/development/code-review-and-sarif.md](../../docs/development/code-review-and-sarif.md) in sync when flags or outputs change.

## Tests

- [src/codomyrmex/tests/unit/scripts/test_review_pipeline.py](../../src/codomyrmex/tests/unit/scripts/test_review_pipeline.py)

## Navigation

- **Parent**: [scripts/AGENTS.md](../AGENTS.md), [scripts/README.md](../README.md)
- **Doc**: [code-review-and-sarif.md](../../docs/development/code-review-and-sarif.md)
- **Project root**: [README.md](../../README.md), [AGENTS.md](../../AGENTS.md)
