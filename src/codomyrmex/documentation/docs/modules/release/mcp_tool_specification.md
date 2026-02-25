# Release Module — MCP Tool Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## Overview

The `release` module does **not** expose any MCP tools. Its components are accessible exclusively via direct Python import.

## Reason

Release validation and package building involve local filesystem operations, subprocess execution, and coordinated multi-step workflows. These are best orchestrated programmatically within CI/CD pipelines and release scripts rather than dispatched as individual agent tool calls.

## Python API

All functionality is available via Python import:

```python
from codomyrmex.release import ReleaseValidator, PackageBuilder, DistributionManager
```

See `API_SPECIFICATION.md` for full class signatures and usage examples.
