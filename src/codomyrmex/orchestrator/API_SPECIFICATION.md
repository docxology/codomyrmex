# Orchestrator Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `orchestrator` module provides a flexible way to discover, configure, and execute Python scripts in the project. It abstracts script execution into a managed "orchestration" layer.

## 2. Core Components

### 2.1 Execution
- **`run_orchestrator()`**: The main entry point for the orchestration CLI.
- **`get_script_config()`**: Retrieves configuration for a specific script.

## 3. Usage Example

```python
from codomyrmex.orchestrator import run_orchestrator

# Launch the interactive orchestrator menu
run_orchestrator()
```
