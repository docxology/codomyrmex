# scripts/review

**Status**: Active | **Last Updated**: March 2026

Local helpers for diff-based review hints, Python structural checks, SARIF merge/summary, and combined Markdown reports. These tools are advisory; they do not replace CI or human review.

## Scripts

| Script | Purpose |
|--------|---------|
| `pr_analyzer.py` | `git diff <base>...<head>` with heuristics (secrets-like literals, SQL concat, debugger, `console.log`, eslint-disable, `: any`, TODO/FIXME). Prints risk band and complexity 1–10. |
| `code_quality_checker.py` | Python AST checks: long functions (>50 lines), large files (>500 lines), many parameters (>5), deep nesting (>4), large classes (>20 methods). |
| `review_report_generator.py` | Optional `--pr-analysis`, `--quality-analysis` JSON, and `--sarif` files → verdict + score + Markdown or text. |
| `sarif_merge.py` | Merge SARIF inputs with dedupe (`-o out.sarif`). |
| `bandit_json_to_sarif.py` | Convert Bandit `-f json` output to SARIF 2.1.0 (used in CI; Bandit has no built-in SARIF formatter). |
| `sarif_utils.py` | Shared load/summarize/merge helpers (stdlib JSON). |

## Usage

Run from repository root with `uv run python scripts/review/<script>.py …` so imports resolve (`sarif_utils` lives in this directory).

```bash
uv run python scripts/review/pr_analyzer.py . --base origin/main --head HEAD
uv run python scripts/review/pr_analyzer.py . --base main --head HEAD --json

uv run python scripts/review/code_quality_checker.py src/codomyrmex --language python --json

uv run python scripts/review/sarif_merge.py a.sarif b.sarif -o merged.sarif

uv run python scripts/review/review_report_generator.py . \
  --pr-analysis pr.json --quality-analysis q.json --sarif merged.sarif \
  --format markdown --output review.md
```

## Navigation

- [AGENTS.md](AGENTS.md) — agent coordination for this directory
- [docs/development/code-review-and-sarif.md](../../docs/development/code-review-and-sarif.md)
- [scripts/README.md](../README.md)
