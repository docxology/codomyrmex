# sandbox

## Signposting
- **Parent**: [coding](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Sandboxing and isolation for secure code execution. Provides Docker container management, process isolation, resource limits enforcement, and security measures for safe code execution.

## Directory Contents
- `README.md` – File
- `__init__.py` – File
- `container.py` – File
- `isolation.py` – File
- `resource_limits.py` – File
- `security.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [coding](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.coding.sandbox import (
    run_code_in_docker,
    ExecutionLimits,
    check_docker_available,
    execute_with_limits,
)

# Check if Docker is available
if check_docker_available():
    # Execute code with resource limits
    limits = ExecutionLimits(
        cpu_time=5.0,
        memory_mb=512,
        max_output_size=1024
    )
    
    result = execute_with_limits(
        code="print('Hello from sandbox')",
        language="python",
        limits=limits
    )
    print(f"Output: {result.output}")
    
    # Or use Docker directly
    docker_result = run_code_in_docker(
        code="import sys; print(sys.version)",
        language="python"
    )
```

