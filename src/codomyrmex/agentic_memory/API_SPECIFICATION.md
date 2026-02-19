# API_SPECIFICATION.md

**Version**: v0.1.7 | **Status**: Draft | **Last Updated**: February 2026

## Module: agentic_memory

### Overview

Long-term agent memory systems for stateful, persistent agent interactions

### Public API

See `__init__.py` for the complete list of exported classes and functions.

### Dependencies

- Python >= 3.10
- See `pyproject.toml` for package dependencies

### Usage

```python
from codomyrmex.agentic_memory import *
```

### Error Handling

All public functions raise standard Python exceptions. Module-specific exceptions inherit from `Exception`.

### Thread Safety

Thread safety varies by component. See individual class documentation for details.

## Navigation

- **Parent**: [README.md](README.md)
- **Project Root**: [../../README.md](../../README.md)
