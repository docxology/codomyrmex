# Accessibility Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

WCAG compliance checking and accessibility utilities.

## Key Features

- **WCAGLevel** — WCAG conformance levels.
- **IssueType** — Types of accessibility issues.
- **AccessibilityIssue** — An accessibility issue.
- **AccessibilityReport** — Accessibility audit report.
- **WCAGRule** — A WCAG accessibility rule.
- **A11yChecker** — Accessibility checker.
- `calculate_contrast_ratio()` — Calculate WCAG contrast ratio between two colors.
- `check_heading_hierarchy()` — Check heading level hierarchy.
- `score()` — score
- `check()` — check

## Quick Start

```python
from codomyrmex.accessibility import WCAGLevel, IssueType, AccessibilityIssue

# Initialize
instance = WCAGLevel()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `WCAGLevel` | WCAG conformance levels. |
| `IssueType` | Types of accessibility issues. |
| `AccessibilityIssue` | An accessibility issue. |
| `AccessibilityReport` | Accessibility audit report. |
| `WCAGRule` | A WCAG accessibility rule. |
| `A11yChecker` | Accessibility checker. |

### Functions

| Function | Description |
|----------|-------------|
| `calculate_contrast_ratio()` | Calculate WCAG contrast ratio between two colors. |
| `check_heading_hierarchy()` | Check heading level hierarchy. |
| `score()` | score |
| `check()` | check |
| `add_rule()` | add rule |
| `check_elements()` | Check a list of elements. |
| `hex_to_luminance()` | hex to luminance |
| `adjust()` | adjust |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k accessibility -v
```

## Navigation

- **Source**: [src/codomyrmex/accessibility/](../../../src/codomyrmex/accessibility/)
- **Parent**: [Modules](../README.md)
