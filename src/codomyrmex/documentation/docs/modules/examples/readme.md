# Examples Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Examples module contains reference implementations and demonstrations that showcase how to use various Codomyrmex capabilities. It includes an agent orchestration demo (parallel execution, sequential execution, circuit breaker patterns) and a REST API endpoint example, along with sample configuration validation and link check output reports.

## PAI Integration

| Algorithm Phase | Examples Role |
|----------------|---------------|
| LEARN | Reference implementations for understanding Codomyrmex patterns |
| BUILD | Code templates and patterns for new feature development |

## Key Exports

The examples module does not export any public classes or functions via `__init__.py`. Examples are accessed by running the scripts directly.

## Quick Start

```bash
# Run the agent orchestration demo
uv run python src/codomyrmex/examples/agent_orchestration_demo.py

# Run the API endpoint example
uv run python src/codomyrmex/examples/api_endpoint_example.py
```

## Architecture

```
examples/
  __init__.py                    # Package marker (no public exports)
  agent_orchestration_demo.py    # Multi-agent orchestration patterns demo
                                 #   - SimulatedAgent (configurable delay/failure)
                                 #   - Parallel execution with ThreadPoolExecutor
                                 #   - Sequential execution
                                 #   - Circuit breaker / fallback strategies
  api_endpoint_example.py        # REST API endpoint creation example
                                 #   - APIRouter with GET/POST endpoints
                                 #   - Request/response handling patterns
  config_validation_report.json  # Sample config validation output
  link_check_report.json         # Sample link check output
  output/                        # Example output directory
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/examples/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) -- Agent coordination documentation
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../examples/)
