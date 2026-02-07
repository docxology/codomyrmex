# Accessibility — Functional Specification

**Module**: `codomyrmex.accessibility`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

WCAG compliance checking and accessibility utilities.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `WCAGLevel` | Class | WCAG conformance levels. |
| `IssueType` | Class | Types of accessibility issues. |
| `AccessibilityIssue` | Class | An accessibility issue. |
| `AccessibilityReport` | Class | Accessibility audit report. |
| `WCAGRule` | Class | A WCAG accessibility rule. |
| `A11yChecker` | Class | Accessibility checker. |
| `calculate_contrast_ratio()` | Function | Calculate WCAG contrast ratio between two colors. |
| `check_heading_hierarchy()` | Function | Check heading level hierarchy. |
| `score()` | Function | score |
| `check()` | Function | check |
| `add_rule()` | Function | add rule |

## 3. Dependencies

See `src/codomyrmex/accessibility/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.accessibility import WCAGLevel, IssueType, AccessibilityIssue, AccessibilityReport, WCAGRule
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k accessibility -v
```
