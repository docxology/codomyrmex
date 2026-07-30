# Documentation quality functional specification

## Components

### RASP audit

`ModuleAudit(path: Path, src_root: Path)` populates missing/placeholder file
lists, `py.typed` presence, module-docstring presence, and top-level Python-file
count.

`audit_documentation(src_dir: Path, report_file: Path) -> None` writes a
Markdown package audit.

`find_rasp_gaps(base_dir: Path) -> dict[str, list[str]]` returns deterministic
missing-file details. `audit_rasp(base_dir: Path) -> int` prints those details
and returns only `0` or `1`.

### Quality assessment

`DocumentationQualityAnalyzer.analyze_file(path)` returns heuristic scores on a
0–100 scale. `generate_quality_report(project_path)` returns Markdown as a
string and does not write it.

### Consistency checking

`DocumentationConsistencyChecker` reports trailing whitespace, tabs, simple
local-link failures, and configured section gaps. It returns
`ConsistencyIssue` and `ConsistencyReport` data classes.

## Requirements

- Read-only functions must not alter source bytes.
- Report-writing functions must write only the caller-provided path.
- Package discovery requires `__init__.py` and excludes hidden/cache paths.
- Finding and path order must be deterministic.
- Missing-file counts must not be confused with audit exit codes.
- Scores and presence checks must not be described as semantic correctness.

## Known scope limits

- The consistency link check is simpler than the repository MkDocs hook and
  comprehensive link validator.
- Quality scores are keyword/structure heuristics.
- Package-native RASP scope differs from the repository README/AGENTS pair
  contract.
- The repository documentation release gate is `make docs-check`.

## Navigation

- [README](README.md)
- [Agent guidance](AGENTS.md)
- [Parent specification](../SPEC.md)
