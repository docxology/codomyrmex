# Accessibility Module

WCAG compliance checking and a11y utilities.

```python
from codomyrmex.accessibility import A11yChecker, WCAGLevel, calculate_contrast_ratio

checker = A11yChecker(level=WCAGLevel.AA)
report = checker.check_elements([
    {"tag": "img", "alt": ""},  # Fail
    {"tag": "a", "text": "Click here"},  # Pass
])
print(f"Score: {report.score:.1f}%")
```
