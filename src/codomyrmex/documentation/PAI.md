# Personal AI Infrastructure — Documentation Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Documentation module provides PAI integration for auto-generating docs from code.

## PAI Capabilities

### Documentation Generation

Generate docs from source:

```python
from codomyrmex.documentation import DocGenerator

generator = DocGenerator()
generator.scan("src/")
generator.generate_api_docs("docs/api/")
```

### Docstring Extraction

Extract and validate docstrings:

```python
from codomyrmex.documentation import DocstringParser

parser = DocstringParser()
docs = parser.extract("src/main.py")

for func in docs.functions:
    print(f"{func.name}: {func.docstring}")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `DocGenerator` | Auto-generate docs |
| `DocstringParser` | Extract docstrings |
| `MarkdownRenderer` | Render markdown |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
