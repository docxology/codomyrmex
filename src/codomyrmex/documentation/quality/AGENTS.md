# Quality Module - Agent Coordination

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides automated documentation quality assessment, RASP compliance auditing, and consistency checking. Agents use this module to measure documentation health, detect placeholder content, and enforce formatting standards across the repository.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `audit.py` | `ModuleAudit` | Audits a single module for RASP file presence, placeholder detection, `py.typed` marker, and `__init__` docstrings |
| `audit.py` | `audit_documentation` | Walks `src/` to audit all modules; returns list of `ModuleAudit` results |
| `audit.py` | `audit_rasp` | RASP-specific audit returning shell exit code (0 = compliant) |
| `audit.py` | `generate_report` | Renders a markdown compliance matrix from audit results |
| `quality_assessment.py` | `DocumentationQualityAnalyzer` | Scores files on completeness, consistency, technical accuracy, readability, and structure |
| `quality_assessment.py` | `generate_quality_report` | Produces an aggregate quality report for a documentation directory |
| `consistency_checker.py` | `ConsistencyIssue` | Dataclass describing a single consistency violation (file, line, type, message) |
| `consistency_checker.py` | `ConsistencyReport` | Dataclass aggregating issues with `total_issues` count |
| `consistency_checker.py` | `DocumentationConsistencyChecker` | Detects trailing whitespace, tab indentation, and naming pattern violations |
| `consistency_checker.py` | `check_documentation_consistency` | Convenience function wrapping `DocumentationConsistencyChecker` |

## Operating Contracts

- `audit_documentation` expects a `src_dir` pointing at the repository source root; it discovers modules by walking subdirectories.
- Placeholder detection looks for sentinel phrases ("TODO", "placeholder", "lorem ipsum") -- modules containing them are flagged non-compliant.
- `DocumentationQualityAnalyzer` returns scores as floats in [0.0, 1.0] per dimension; `_calculate_overall_score` aggregates via weighted average.
- Consistency checks are non-destructive (read-only); fixes are handled by `documentation/scripts`.

## Integration Points

- `documentation/scripts` -- fixer scripts consume audit and consistency results to apply automated repairs.
- `maintenance` -- `maintenance_health_check` can invoke quality audits as part of system health assessment.
- `model_context_protocol` -- `audit_rasp_compliance` is exposed as an MCP tool via `@mcp_tool`.

## Navigation

- **Parent**: [../README.md](../README.md)
- **Siblings**: [../education/AGENTS.md](../education/AGENTS.md) | [../scripts/AGENTS.md](../scripts/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
