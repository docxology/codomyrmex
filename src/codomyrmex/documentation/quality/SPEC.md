# Quality Module - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements three complementary documentation health strategies: RASP compliance auditing (`audit.py`), multi-dimensional quality scoring (`quality_assessment.py`), and formatting consistency checking (`consistency_checker.py`). All operations are read-only analysis; repairs are delegated to `documentation/scripts`.

## Architecture

Each analyser is self-contained. `ModuleAudit` checks structural compliance (file existence, placeholder markers). `DocumentationQualityAnalyzer` applies five weighted scoring dimensions. `DocumentationConsistencyChecker` performs line-level formatting checks. Results are returned as dataclasses or dicts; no files are modified.

## Key Classes

### `ModuleAudit`

| Method / Attribute | Description |
|--------------------|-------------|
| `module_path` | Path to the module directory being audited |
| `has_readme` | Whether `README.md` exists |
| `has_agents` | Whether `AGENTS.md` exists |
| `has_spec` | Whether `SPEC.md` exists |
| `has_pai` | Whether `PAI.md` exists |
| `has_py_typed` | Whether `py.typed` marker exists |
| `has_init_docstring` | Whether `__init__.py` has a module docstring |
| `placeholder_detected` | Whether placeholder sentinels were found |

### `DocumentationQualityAnalyzer`

| Method | Description |
|--------|-------------|
| `analyze_file(path)` | Score a single markdown file; returns dict with per-dimension and overall scores |
| `_assess_completeness(content)` | Checks heading count, word count, section presence |
| `_assess_consistency(content)` | Checks heading style consistency, list formatting |
| `_assess_technical_accuracy(content)` | Checks code block presence, link validity patterns |
| `_assess_readability(content)` | Sentence length, paragraph structure |
| `_assess_structure(content)` | Heading hierarchy, navigation section presence |
| `_calculate_overall_score(scores)` | Weighted average across all five dimensions |

### `DocumentationConsistencyChecker`

| Method | Description |
|--------|-------------|
| `check_file(path)` | Returns list of `ConsistencyIssue` for one file |
| `check_directory(path)` | Recursively checks all `.md` files; returns `ConsistencyReport` |

### `ConsistencyIssue` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Relative path of the file |
| `line_number` | `int` | Line where issue was found |
| `issue_type` | `str` | Category (e.g., `"trailing_whitespace"`, `"tab_indentation"`) |
| `message` | `str` | Human-readable description |

### Top-level Functions

| Function | Description |
|----------|-------------|
| `audit_documentation(src_dir)` | Walk source tree, return `list[ModuleAudit]` |
| `audit_rasp(src_dir)` | RASP audit returning exit code 0 (pass) or 1 (fail) |
| `generate_report(audits)` | Markdown compliance matrix string |
| `generate_quality_report(docs_dir)` | Aggregate quality report dict |
| `check_documentation_consistency(path)` | Convenience wrapper returning `ConsistencyReport` |

## Dependencies

- `logging_monitoring` -- structured logging via `get_logger`.
- Standard library: `pathlib`, `dataclasses`, `re`, `os`.

## Constraints

- All operations are read-only; no files are written or modified.
- Quality scores are floats in `[0.0, 1.0]`; overall score uses equal weighting unless overridden.
- Consistency checks skip hidden directories and `__pycache__`.

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Missing `src_dir` | `FileNotFoundError` propagated |
| Unreadable file (encoding) | Logged warning; file skipped |
| Permission denied | Logged warning; directory skipped |

## Navigation

- **Parent**: [../README.md](../README.md)
- **Siblings**: [../education/SPEC.md](../education/SPEC.md) | [../scripts/SPEC.md](../scripts/SPEC.md)
- **Root**: [../../../../README.md](../../../../README.md)
