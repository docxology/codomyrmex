# Static Analysis Tutorials

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for running static analysis and code quality checks.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Running Linters](#running-linters) | Run code linters |
| [Type Checking](#type-checking) | Run type checker |
| [Complexity](#complexity) | Analyze code complexity |

## Running Linters

```python
from codomyrmex.static_analysis import LintRunner

# Run ruff
linter = LintRunner(tool="ruff")
issues = linter.run("src/")

for issue in issues:
    print(f"{issue.file}:{issue.line} - {issue.message}")
```

## Type Checking

```python
from codomyrmex.static_analysis import TypeChecker

# Run mypy
checker = TypeChecker()
errors = checker.check("src/")

for error in errors:
    print(f"{error.file}:{error.line} - {error.message}")
```

## Complexity

```python
from codomyrmex.static_analysis import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
report = analyzer.analyze("src/main.py")

for func in report.functions:
    print(f"{func.name}: complexity={func.complexity}")
    if func.complexity > 10:
        print("  ⚠️ Consider refactoring")
```

## Navigation

- **Parent**: [Static Analysis Documentation](../README.md)
- **Source**: [src/codomyrmex/static_analysis/](../../../../src/codomyrmex/static_analysis/)
