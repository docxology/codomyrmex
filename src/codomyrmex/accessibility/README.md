# Accessibility Module

**Version**: v0.1.0 | **Status**: Active

WCAG compliance checking and accessibility utilities.

## Quick Start

```python
from codomyrmex.accessibility import A11yChecker, WCAGLevel, calculate_contrast_ratio

# Create checker at WCAG AA level
checker = A11yChecker(level=WCAGLevel.AA)

# Check elements
elements = [
    {"tag": "img", "selector": "#logo"},  # Missing alt
    {"tag": "img", "alt": "Logo", "selector": "#hero"},
    {"tag": "a", "text": "", "selector": ".btn"},  # Empty link text
]
report = checker.check_elements(elements)

print(f"Score: {report.score:.1f}%")
print(f"Errors: {report.errors}, Warnings: {report.warnings}")

# Check color contrast
ratio = calculate_contrast_ratio("#333333", "#ffffff")
print(f"Contrast ratio: {ratio:.2f}:1")  # 12.63:1
```

## Exports

| Class/Function | Description |
|----------------|-------------|
| `A11yChecker` | WCAG accessibility checker with configurable level |
| `WCAGLevel` | Enum: A, AA, AAA conformance levels |
| `WCAGRule` | Define custom accessibility rules |
| `AccessibilityIssue` | Single accessibility issue with fix suggestion |
| `AccessibilityReport` | Audit report with score, errors, warnings |
| `IssueType` | Enum: error, warning, notice |
| `calculate_contrast_ratio` | WCAG contrast ratio between two hex colors |
| `check_heading_hierarchy` | Validate heading levels (h1, h2, h3...) |

## Built-in Rules

- **img-alt** (1.1.1): Images must have alt text
- **form-label** (1.3.1): Form elements must have labels
- **link-text** (2.4.4): Links must have descriptive text
- **color-contrast** (1.4.3): Text must have 4.5:1 contrast ratio
- **focus-visible** (2.4.7): Interactive elements need focus indicator

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
