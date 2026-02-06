# Pattern Matching Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Pattern matching for text, regex, and AST-based code matching.

## Key Features

- **Text Patterns** — Glob and wildcard
- **Regex** — Regular expressions
- **AST Matching** — Python AST patterns
- **Extraction** — Capture groups

## Quick Start

```python
from codomyrmex.pattern_matching import PatternMatcher, ASTMatcher

matcher = PatternMatcher()
if matcher.matches(text, "def *(*):"):
    print("Found function")

ast = ASTMatcher()
functions = ast.find_all(code, "FunctionDef")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/pattern_matching/](../../../src/codomyrmex/pattern_matching/)
- **Parent**: [Modules](../README.md)
