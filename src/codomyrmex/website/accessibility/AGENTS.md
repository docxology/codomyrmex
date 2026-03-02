# Codomyrmex Agents -- src/codomyrmex/website/accessibility

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides WCAG-compliant accessibility auditing for web content, including a rule-based element checker, data models for issues and reports, multi-format report output (summary, JSON, Markdown), and utility functions for contrast ratio calculation and heading hierarchy validation.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `WCAGLevel`, `IssueType` | Enums for WCAG conformance levels (A, AA, AAA) and issue severity (error, warning, notice) |
| `models.py` | `AccessibilityIssue` | Dataclass for a single accessibility issue with WCAG criterion, level, selector, and remediation suggestion |
| `models.py` | `AccessibilityReport` | Audit report aggregating issues with pass/error/warning counts and a computed percentage score |
| `models.py` | `WCAGRule` | Rule definition binding a WCAG criterion code and level to a check function; returns `AccessibilityIssue` on failure |
| `checker.py` | `A11yChecker` | Rule-based accessibility checker with 5 built-in rules (img-alt, form-label, link-text, color-contrast, focus-visible); supports custom rules and level-filtered checking |
| `reporters.py` | `AccessibilityReporter` | Multi-format report formatter producing one-line summary, serializable dict, JSON string, and Markdown table output |
| `utils.py` | `calculate_contrast_ratio` | WCAG contrast ratio calculator using relative luminance from hex color values |
| `utils.py` | `check_heading_hierarchy` | Validates heading level hierarchy (no skipped levels, must start with h1) |

## Operating Contracts

- `A11yChecker` filters rules by target WCAG level: at level A only level-A rules run; at level AA, both A and AA rules run; at AAA all rules run.
- `WCAGRule.check` returns `None` on pass and an `AccessibilityIssue` on failure; the checker aggregates issues into an `AccessibilityReport`.
- `AccessibilityReport.score` is computed as `(passed / (passed + errors)) * 100`; reports with zero checks score 100.0.
- `calculate_contrast_ratio` follows the WCAG 2.0 relative luminance formula with gamma correction; returns 0.0 on invalid hex input.
- Errors must be logged via `logging` before re-raising.

## Integration Points

- **Depends on**: Python standard library (`json`, `logging`, `dataclasses`, `enum`)
- **Used by**: `website.generator` (site-level accessibility audits), website quality pipelines

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
