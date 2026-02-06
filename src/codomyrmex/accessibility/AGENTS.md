# Agent Guidelines - Accessibility

## Module Overview

WCAG compliance checking, contrast analysis, and accessibility reporting.

## Key Classes

- **A11yChecker** — Check WCAG compliance
- **AccessibilityReport** — Detailed findings report
- **WCAGLevel** — Enum: A, AA, AAA
- **calculate_contrast_ratio()** — Color contrast calculation

## Agent Instructions

1. **Check early** — Validate during development
2. **Target AA** — WCAG 2.1 AA is standard
3. **Test contrast** — 4.5:1 for normal text
4. **Use landmarks** — Add ARIA landmarks
5. **Report all** — Don't hide issues

## Common Patterns

```python
from codomyrmex.accessibility import (
    A11yChecker, calculate_contrast_ratio, WCAGLevel
)

# Check HTML for accessibility
checker = A11yChecker()
report = checker.check(html_content, level=WCAGLevel.AA)

print(f"Passed: {report.passed}")
for issue in report.issues:
    print(f"{issue.severity}: {issue.message}")

# Check color contrast
ratio = calculate_contrast_ratio("#ffffff", "#777777")
print(f"Contrast: {ratio:.2f}:1")
if ratio < 4.5:
    print("Warning: Insufficient contrast for normal text")
```

## Testing Patterns

```python
# Verify contrast calculation
ratio = calculate_contrast_ratio("#000000", "#ffffff")
assert ratio == 21.0  # Maximum contrast

# Verify checker
checker = A11yChecker()
report = checker.check("<img src='x'>")  # Missing alt
assert not report.passed
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
