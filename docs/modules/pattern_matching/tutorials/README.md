# Pattern Matching Tutorials

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for using pattern matching utilities for text and AST matching.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Text Patterns](#text-patterns) | Match text patterns |
| [Regex Helpers](#regex-helpers) | Build regex patterns |
| [AST Matching](#ast-matching) | Match code structures |

## Text Patterns

```python
from codomyrmex.pattern_matching import PatternMatcher

matcher = PatternMatcher()

# Simple pattern
if matcher.matches(text, "def *(*):"):
    print("Found function definition")

# Extract groups
result = matcher.extract(text, r"def (\w+)\((.*?)\)")
print(f"Function: {result.group(1)}")
```

## Regex Helpers

```python
from codomyrmex.pattern_matching import RegexBuilder

# Build pattern fluently
pattern = (RegexBuilder()
    .literal("def ")
    .word()
    .literal("(")
    .any()
    .literal(")")
    .build()
)
```

## AST Matching

```python
from codomyrmex.pattern_matching import ASTMatcher

matcher = ASTMatcher()
functions = matcher.find_all(code, "FunctionDef")

for func in functions:
    print(f"{func.name}: {len(func.args)} args")
```

## Navigation

- **Parent**: [Pattern Matching Documentation](../README.md)
- **Source**: [src/codomyrmex/pattern_matching/](../../../../src/codomyrmex/pattern_matching/)
