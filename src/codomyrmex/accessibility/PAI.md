# Personal AI Infrastructure — Accessibility Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Accessibility module provides PAI integration for WCAG compliance checking and accessibility auditing, enabling AI agents to create inclusive applications.

## PAI Capabilities

### Accessibility Checking

Run accessibility audits as part of AI workflows:

```python
from codomyrmex.accessibility import A11yChecker, WCAGLevel

# Initialize checker
checker = A11yChecker(level=WCAGLevel.AA)

# Audit HTML content
report = checker.audit(html_content)

for issue in report.issues:
    print(f"{issue.severity}: {issue.message}")
    print(f"  Fix: {issue.remediation}")
```

### Color Contrast Analysis

Verify color combinations meet WCAG standards:

```python
from codomyrmex.accessibility import calculate_contrast_ratio

# Check contrast
ratio = calculate_contrast_ratio("#333333", "#FFFFFF")
print(f"Contrast ratio: {ratio:.2f}:1")

# AA requires 4.5:1 for normal text
if ratio >= 4.5:
    print("✓ Passes WCAG AA")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `A11yChecker` | Automated accessibility testing |
| `WCAGRule` | Custom rule definitions |
| `AccessibilityReport` | Generate reports for review |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
