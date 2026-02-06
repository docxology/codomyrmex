# Personal AI Infrastructure — Pattern Matching Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Pattern Matching module provides PAI integration for code and text pattern matching.

## PAI Capabilities

### Code Pattern Matching

Find code patterns:

```python
from codomyrmex.pattern_matching import ASTMatcher

matcher = ASTMatcher()
functions = matcher.find_all(code, "FunctionDef")

for func in functions:
    print(f"{func.name}: {len(func.args)} args")
```

### Text Matching

Match text patterns:

```python
from codomyrmex.pattern_matching import PatternMatcher

matcher = PatternMatcher()
if matcher.matches(text, "def *(*):"):
    print("Found function definition")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `ASTMatcher` | Code analysis |
| `PatternMatcher` | Text matching |
| `RegexBuilder` | Build patterns |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
