# Docs Gen Module — MCP Tool Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## Overview

The `docs_gen` module does **not** expose any MCP tools. Its components are accessible exclusively via direct Python import.

## Reason

Documentation generation operates on Python source strings and produces structured data objects (dataclasses, dicts, Markdown strings). These are best consumed programmatically within build pipelines and CI/CD workflows rather than dispatched via agent tool calls.

## Python API

All functionality is available via Python import:

```python
from codomyrmex.docs_gen import APIDocExtractor, SearchIndex, SiteGenerator
```

See `API_SPECIFICATION.md` for full class signatures and usage examples.
