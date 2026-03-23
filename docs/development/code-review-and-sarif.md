# Code review and SARIF triage

**Status**: Active | **Last Updated**: March 2026

Local workflows for reviewing diffs and inspecting static-analysis results in SARIF 2.1.0 format. CI runs Bandit with JSON output, then converts to SARIF with [`scripts/review/bandit_json_to_sarif.py`](../../scripts/review/bandit_json_to_sarif.py) before upload (Bandit’s CLI does not ship a `-f sarif` formatter). CodeQL and Semgrep integrate with GitHub Security or Semgrep Cloud separately.

## PR and diff review

1. Update your base branch: `git fetch origin main` (or `develop`).
2. Inspect changes: `git diff origin/main...HEAD` (three-dot compares merge base to HEAD).
3. Optional — structured analyzer (heuristics + risk score):

   ```bash
   uv run python scripts/review/pr_analyzer.py . --base origin/main --head HEAD
   uv run python scripts/review/pr_analyzer.py . --base origin/main --head HEAD --json > pr-analysis.json
   ```

4. Optional — Python structural checks (function length, nesting, parameters):

   ```bash
   uv run python scripts/review/code_quality_checker.py src/codomyrmex --language python
   uv run python scripts/review/code_quality_checker.py src/codomyrmex --language python --json > quality.json
   ```

5. Combined Markdown report (optional inputs):

   ```bash
   uv run python scripts/review/review_report_generator.py . \
     --pr-analysis pr-analysis.json \
     --quality-analysis quality.json \
     --sarif bandit-results.sarif \
     --format markdown --output review.md
   ```

See [scripts/review/README.md](../../scripts/review/README.md) for flags and behavior.

## SARIF from CI artifacts

After a workflow run, download the **`bandit-scan-results`** artifact. It includes `bandit-results.sarif` (converted from Bandit JSON), plus JSON, text, and XML reports.

### With sarif-tools (dev dependency)

After `uv sync --dev`:

```bash
uv run sarif summary bandit-results.sarif
uv run sarif ls --level error bandit-results.sarif
uv run sarif html bandit-results.sarif > bandit-report.html
```

Compare two runs for regressions:

```bash
uv run sarif diff baseline.sarif bandit-results.sarif
```

### With jq

```bash
jq '[.runs[].results[]] | length' bandit-results.sarif
jq '[.runs[].results[].ruleId] | unique' bandit-results.sarif
jq '.runs[].results[] | select(.level == "error") | {rule: .ruleId, msg: .message.text}' bandit-results.sarif
```

Paths inside SARIF may be relative or `file://` URIs; normalize before matching local files.

## Merging multiple SARIF files

For offline aggregation (e.g. several downloaded artifacts):

```bash
uv run python scripts/review/sarif_merge.py one.sarif two.sarif -o merged.sarif
```

Dedupe uses `ruleId`, artifact URI, and `startLine` when fingerprints are absent.

## Scope

- **CodeQL** and **Semgrep** findings are primarily visible in GitHub’s Security tab or Semgrep’s UI; this document focuses on **local** triage of files you have on disk.
- Scripts are advisory heuristics, not a substitute for human review or policy gates.

## Navigation

- **Parent**: [development/](README.md) — developer guides  
- **Contributing**: [../project/contributing.md](../project/contributing.md)  
- **Security workflow**: [../../.github/workflows/security.yml](../../.github/workflows/security.yml)
