# Accessibility Module — Agent Coordination

## Purpose

WCAG compliance checking and accessibility utilities.

## Key Capabilities

- **WCAGLevel**: WCAG conformance levels.
- **IssueType**: Types of accessibility issues.
- **AccessibilityIssue**: An accessibility issue.
- **AccessibilityReport**: Accessibility audit report.
- **WCAGRule**: A WCAG accessibility rule.
- `calculate_contrast_ratio()`: Calculate WCAG contrast ratio between two colors.
- `check_heading_hierarchy()`: Check heading level hierarchy.
- `score()`: score

## Agent Usage Patterns

```python
from codomyrmex.accessibility import WCAGLevel

# Agent initializes accessibility
instance = WCAGLevel()
```

## Integration Points

- **Source**: [src/codomyrmex/accessibility/](../../../src/codomyrmex/accessibility/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k accessibility -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
