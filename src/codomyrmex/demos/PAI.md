# Personal AI Infrastructure -- Demos Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demo registry and execution system for running and managing demonstration scripts. Provides `DemoRegistry` for discovering, registering, and executing demos with structured results.

## PAI Capabilities

### Demo Discovery and Execution

```python
from codomyrmex.demos import DemoRegistry, DemoInfo, DemoResult

registry = DemoRegistry()
available: list[DemoInfo] = registry.list_demos()

result: DemoResult = registry.run_demo("example_demo")
print(f"Status: {result.status}, Output: {result.output}")
```

## PAI Phase Mapping

| Phase   | Tool/Class   | Usage                                     |
|---------|--------------|-------------------------------------------|
| EXECUTE | DemoRegistry | Run registered demos and collect results   |

## Key Exports

| Export       | Type      | Description                          |
|--------------|-----------|--------------------------------------|
| DemoRegistry | Class     | Demo discovery, registration, runner |
| DemoInfo     | Dataclass | Metadata about a registered demo     |
| DemoResult   | Dataclass | Execution outcome from a demo run    |

## Integration Notes

- Exposed via `mcp_tools.py` to allow AI agents to list and run demos.
- Used internally for validating module capabilities via demonstration scripts.
- Call directly from Python when PAI agents need to run or list demos.
