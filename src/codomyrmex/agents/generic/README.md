# generic

## Signposting
- **Parent**: [agents](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Base agent classes and utilities. Provides abstract base classes for all agents, agent orchestration, message bus for inter-agent communication, and task planning capabilities. Serves as the foundation for all agent implementations.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `agent_orchestrator.py` – File
- `base_agent.py` – File
- `message_bus.py` – File
- `task_planner.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [agents](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.agents.generic import (
    BaseAgent,
    AgentOrchestrator,
    MessageBus,
    TaskPlanner,
)

# Create a base agent
class MyAgent(BaseAgent):
    def execute(self, task):
        return f"Executed: {task}"

agent = MyAgent(name="my_agent", capabilities=["task_execution"])

# Use agent orchestrator
orchestrator = AgentOrchestrator()
orchestrator.add_agent(agent)
result = orchestrator.execute_parallel([{"task": "task1"}, {"task": "task2"}])

# Use message bus for inter-agent communication
bus = MessageBus()
bus.subscribe("task_complete", lambda msg: print(f"Task complete: {msg}"))
bus.publish("task_complete", {"task_id": "123"})

# Use task planner
planner = TaskPlanner()
plan = planner.create_plan(goal="Build API", context={})
```

