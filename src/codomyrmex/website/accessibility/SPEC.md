# Accessibility -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

WCAG conformance checking engine with configurable rules, structured reporting, and color contrast utilities. The checker applies rules filtered by target WCAG level and produces scored reports.

## Architecture

```
A11yChecker(level: WCAGLevel)
  +-- rules: list[WCAGRule]
  +-- add_rule(rule)
  +-- check_elements(elements) -> AccessibilityReport

AccessibilityReport
  +-- issues: list[AccessibilityIssue]
  +-- passed / errors / warnings
  +-- score: float (0-100)

AccessibilityReporter(report)
  +-- to_summary() -> str
  +-- to_dict() -> dict
  +-- to_json() -> str
  +-- to_markdown() -> str
```

## Key Classes

### A11yChecker

| Method | Returns | Description |
|--------|---------|-------------|
| `add_rule(rule)` | `None` | Register custom WCAG rule |
| `check_elements(elements)` | `AccessibilityReport` | Apply rules at/below target level |

### Default Rules

| Code | WCAG Criterion | Level | Check |
|------|---------------|-------|-------|
| `img-alt` | 1.1.1 | A | Images must have alt text |
| `form-label` | 1.3.1 | A | Form inputs must have labels |
| `link-text` | 2.4.4 | A | Links must have descriptive text |
| `color-contrast` | 1.4.3 | AA | Foreground/background contrast >= 4.5:1 |
| `focus-visible` | 2.4.7 | AA | Interactive elements must have focus indicators |

### AccessibilityIssue

| Field | Type | Notes |
|-------|------|-------|
| `code` | `str` | Rule code (e.g., `"img-alt"`) |
| `message` | `str` | Human-readable description |
| `selector` | `str` | CSS selector or element identifier |
| `wcag_criterion` | `str` | WCAG success criterion (e.g., `"1.1.1"`) |
| `wcag_level` | `WCAGLevel` | A, AA, or AAA |
| `suggestion` | `str` | Remediation guidance |

### Utility Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `calculate_contrast_ratio(fg, bg)` | `float` | WCAG luminance contrast ratio |
| `check_heading_hierarchy(headings)` | `list[str]` | Sequence violations (e.g., h1 -> h3 skip) |

## Dependencies

- `enum`, `dataclasses`, `json`, `math` (stdlib)

## Constraints

- Rules are Python callables; no CSS selector engine or DOM parser included.
- Color contrast requires hex color strings; no named-color lookup.
- Heading hierarchy check expects ordered `list[int]` of heading levels.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [website](../README.md)
