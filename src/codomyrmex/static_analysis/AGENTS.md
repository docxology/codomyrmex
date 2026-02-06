# Agent Guidelines - Static Analysis

## Module Overview

Code analysis: linting, type checking, complexity, and security scanning.

## Key Classes

- **Analyzer** — Run static analysis
- **LintRunner** — Run linters (ruff, flake8)
- **TypeChecker** — Type checking (mypy)
- **ComplexityAnalyzer** — Cyclomatic complexity

## Agent Instructions

1. **Run on save** — Fast feedback loop
2. **Fix incrementally** — Don't fix all at once
3. **Configure rules** — Adjust to project needs
4. **Track metrics** — Complexity trends
5. **Block on errors** — No commits with errors

## Common Patterns

```python
from codomyrmex.static_analysis import (
    Analyzer, LintRunner, TypeChecker, ComplexityAnalyzer
)

# Full analysis
analyzer = Analyzer()
report = analyzer.analyze("src/")

for issue in report.issues:
    print(f"{issue.file}:{issue.line} - {issue.message}")

# Lint specifically
linter = LintRunner(tool="ruff")
issues = linter.run("src/main.py")

# Type checking
types = TypeChecker()
errors = types.check("src/")

# Complexity
complexity = ComplexityAnalyzer()
scores = complexity.analyze("src/main.py")
```

## Testing Patterns

```python
# Verify analysis runs
analyzer = Analyzer()
report = analyzer.analyze("src/")
assert report is not None

# Verify clean code passes
code = "def foo(): return 1"
issues = LintRunner().check_string(code)
assert len(issues) == 0
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
