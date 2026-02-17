# Agent Guidelines - Coding

**Version**: v0.4.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Unified toolkit for code execution, analysis, review, and transformation.

## Key Classes

- **CodeReviewer** — Orchestrate code quality reviews
- **StaticAnalyzer** — Run deep linting and complexity analysis
- **PatternMatcher** — Search for structural patterns (AST-based)
- **CodeGenerator** — Generate code from functional specs
- **Debugger** — Automated error diagnosis and patching

## Agent Instructions

1. **Analyze before fix** — Use `StaticAnalyzer` to verify code quality before suggesting fixes
2. **Structural Search** — Use `PatternMatcher` to find all instances of a pattern before refactoring
3. **Sandbox execution** — Always use `coding.execution` for untrusted code
4. **Metric-driven review** — Check `CodeMetrics` during reviews

## Common Patterns

```python
from codomyrmex.coding import (
    CodeReviewer, StaticAnalyzer, PatternMatcher, Debugger
)

# Deep Static Analysis
analyzer = StaticAnalyzer()
results = analyzer.analyze_project("./src")
print(f"Complexity: {results.complexity}")

# Find occurrences of a pattern
matcher = PatternMatcher()
occurrences = matcher.find_pattern(
    "Assignment(target=Name(id='x'), value=Constant(value=1))"
)

# Automated Debug Loop
debugger = Debugger()
diagnosis = debugger.diagnose(failing_script_path)
if diagnosis.can_fix:
    patch = debugger.generate_patch(diagnosis)
    debugger.apply_and_verify(patch)
```

## Testing Patterns

```python
# Verify static analysis findings
analyzer = StaticAnalyzer()
results = analyzer.analyze_file("bad_code.py")
assert any(r.type == "Complexity" for r in results)

# Verify pattern matching
matcher = PatternMatcher()
matches = matcher.find_in_string("x = 10", "Assignment")
assert len(matches) == 1
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
