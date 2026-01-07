# logging_monitoring

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Centralized logging infrastructure for the Codomyrmex platform. Implements unified logging system with consistent formatting, configurable output destinations (console, file), configurable log levels, JSON and text formatters, and proper log level management. Provides singleton-like configuration ensuring logging is set up once for the entire application.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `logger_config.py` – File
- `requirements.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.logging_monitoring import (
    setup_logging,
    get_logger,
    log_context,
)

# Setup logging
setup_logging(
    level="INFO",
    format="json",  # or "text"
    output="console"  # or "file"
)

# Get logger
logger = get_logger(__name__)
logger.info("Application started")
logger.debug("Debug information")
logger.error("Error occurred", exc_info=True)

# Use log context
with log_context(operation="process_data", user_id="123"):
    logger.info("Processing data")
    # All logs within this context will include operation and user_id
```

