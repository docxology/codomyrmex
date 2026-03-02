# Codomyrmex Agents — src/codomyrmex/agents/specialized

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Autonomous code improvement subsystem that detects anti-patterns via regex-based analysis, proposes fixes with confidence scoring, generates regression tests, and renders markdown improvement reports. Also provides a generate-test-review loop for iterative code generation convergence.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `improvement_pipeline.py` | `ImprovementPipeline` | Full cycle: analyze anti-patterns -> generate fixes -> generate tests -> review verdict |
| `improvement_pipeline.py` | `AntiPatternDetector` | Regex-based scanner for bare_except, mutable_default, star_import, print_debug, todo_fixme |
| `improvement_report.py` | `ImprovementReport` | Complete report with anti-patterns, proposed changes, test results, verdict, markdown rendering |
| `improvement_report.py` | `AntiPattern` | Detected pattern with name, severity, file path, line range, snippet |
| `improvement_report.py` | `ProposedChange` | Proposed fix with old/new code, rationale, confidence, risk level |
| `improvement_report.py` | `ReviewVerdict` / `RiskLevel` | Enums: APPROVE/REJECT/REVISE and LOW/MEDIUM/HIGH/CRITICAL |
| `improvement_report.py` | `TestSuiteResult` | Test generation results: total, passed, failed, errors, test source code |
| `improvement_config.py` | `ImprovementConfig` | Safety limits: max_changes_per_run, min_confidence, severity_threshold, auto_apply flag |
| `review_loop.py` | `ReviewLoop` | Generate -> test -> review cycle using `CodeGenerator` and `TestGenerator` until approval |
| `review_loop.py` | `ReviewResult` / `ReviewLoopResult` | Iteration result and overall convergence status |

## Operating Contracts

- `AntiPatternDetector` ships with 5 built-in patterns: bare_except (0.7), mutable_default (0.8), star_import (0.5), print_debug (0.3), todo_fixme (0.2). Severity threshold filters patterns below the configured floor.
- `ImprovementPipeline.improve()` enforces `max_changes_per_run` and `min_confidence` gates. Only changes with confidence >= threshold are proposed.
- Review verdict is APPROVE when average confidence >= min_confidence, REVISE when below threshold, REJECT when no changes were generated.
- `ReviewLoop._review()` uses a 4-criterion scoring system: has functions (+0.3), has tests (+0.3), compiles (+0.2), reasonable size (+0.2). Approval at >= 0.7 by default.
- `ImprovementReport.to_markdown()` renders diff-formatted output with anti-patterns, proposed changes, and test results.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`, `codomyrmex.coding.generator.CodeGenerator`, `codomyrmex.coding.test_generator.TestGenerator`
- **Used by**: Agent improvement workflows, PAI VERIFY phase post-processing

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
