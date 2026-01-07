# environment_setup

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [scripts](scripts/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Ensures the Codomyrmex platform runs in a deterministic, validated environment. Acts as the "gatekeeper" at startup, verifying dependencies, Python versions, and configuration integrity before any other module is allowed to execute. Provides fail-fast validation with helpful error messages guiding users to solutions.

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
- `env_checker.py` – File
- `requirements.txt` – File
- `scripts/` – Subdirectory
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.environment_setup import (
    validate_python_version,
    check_and_setup_env_vars,
    ensure_dependencies_installed,
    is_uv_available,
)

# Validate Python version
if not validate_python_version(min_version="3.10"):
    raise RuntimeError("Python 3.10+ required")

# Check if uv is available
if is_uv_available():
    print("Using uv for dependency management")
else:
    print("uv not available, using pip")

# Setup environment variables
check_and_setup_env_vars({
    "CODOMYRMEX_LOG_LEVEL": "INFO",
    "CODOMYRMEX_CACHE_DIR": ".cache"
})

# Ensure dependencies are installed
ensure_dependencies_installed(["requests", "pydantic"])
```

