# Personal AI Infrastructure -- Examples Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Examples module contains runnable demonstration scripts that showcase how to use
Codomyrmex capabilities end-to-end. Each example is a self-contained Python file
that imports real module interfaces, exercises them, and prints observable results.
The module intentionally exports nothing (`__all__ = []`) -- its value is as
living reference code, not as a library dependency.

## Available Examples

| File | What It Demonstrates |
|------|---------------------|
| `agent_orchestration_demo.py` | Parallel execution, sequential execution, and fallback strategies using `AgentOrchestrator` |

### agent_orchestration_demo.py

This is the primary example file. It exercises three orchestration patterns from the
`codomyrmex.agents` module:

1. **Parallel Execution** -- Three `SimulatedAgent` instances run concurrently via
   `ThreadPoolExecutor`. Expected wall-clock time is ~1 s for three agents that
   each take 1 s individually.
2. **Sequential Execution** -- Two agents process in order, demonstrating
   deterministic one-after-another dispatch.
3. **Fallback Strategy** -- An unreliable agent (100 % failure rate) is paired
   with a reliable agent. `execute_with_fallback` tries each in order until
   one succeeds, implementing a circuit-breaker pattern.

Key imports used by the demo:

```python
from codomyrmex.agents import (
    AgentCapabilities,
    AgentInterface,
    AgentOrchestrator,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.logging_monitoring import get_logger, setup_logging
```

Running the demo:

```bash
uv run python src/codomyrmex/examples/agent_orchestration_demo.py
```

## PAI Capabilities

### Reference Implementation Patterns

The examples module gives PAI agents concrete, tested patterns to follow when:

- Composing multi-agent workflows (parallel, sequential, fallback)
- Implementing the `AgentInterface` abstract class with custom behavior
- Using `setup_logging` for structured output in agent scripts
- Handling failures gracefully without mocks or stubs

### Validation Target

PAI can execute examples as smoke tests to verify that the agents module and
its orchestration layer are functional. Because every example uses real imports
and real runtime behavior, a passing run confirms the integration surface is
healthy.

## PAI Algorithm Phase Mapping

| Phase | Examples Contribution | How |
|-------|-----------------------|-----|
| **OBSERVE** | Codebase pattern discovery | PAI reads example files to learn established usage patterns |
| **THINK** | Capability assessment | Examples confirm which orchestration patterns are available |
| **PLAN** | Workflow template selection | Example workflows serve as templates for PAI plan construction |
| **BUILD** | Reference code for generation | When generating new orchestration code, PAI can reference these examples |
| **EXECUTE** | Smoke-test execution | PAI runs examples to validate agent infrastructure health |
| **VERIFY** | Integration validation | A passing demo run confirms `AgentOrchestrator`, `AgentInterface`, and logging work |
| **LEARN** | Pattern catalog | Examples contribute tested patterns to PAI's knowledge of codomyrmex |

## Key Classes in agent_orchestration_demo.py

| Class/Function | Role |
|----------------|------|
| `SimulatedAgent` | Concrete `AgentInterface` with configurable delay and failure rate |
| `main()` | Entry point that runs all three demos in sequence |

`SimulatedAgent` implements the full `AgentInterface` contract:
`execute()`, `stream()`, `setup()`, `test_connection()`, `get_capabilities()`,
and `supports_capability()`.

## Architecture Role

**Specialized Layer** -- Examples sit in the Specialized layer and import from
Core and Foundation modules (agents, logging_monitoring). They do not expose
MCP tools or contribute to the runtime dependency graph.

```
examples/
  __init__.py                    # __all__ = [] (no exports)
  agent_orchestration_demo.py    # Runnable demo script
```

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `agents` | Examples consume `AgentInterface`, `AgentOrchestrator`, `AgentRequest`, `AgentResponse` |
| `logging_monitoring` | Examples use `get_logger` and `setup_logging` for structured output |
| `orchestrator` | The orchestration demo patterns mirror the workflow patterns available in the orchestrator module |

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
