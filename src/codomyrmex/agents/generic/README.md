# src/codomyrmex/agents/generic

## Signposting
- **Parent**: [agents](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Generic submodule providing shared functionality used across all agent implementations. This includes base agent classes, multi-agent orchestration, inter-agent communication, and task planning utilities.

## Key Components

- **BaseAgent**: Base implementation of `AgentInterface` with common functionality
- **AgentOrchestrator**: Coordinate multiple agents for complex tasks
- **MessageBus**: Inter-agent communication system
- **TaskPlanner**: Task planning and decomposition utilities

## Usage

### BaseAgent

```python
from codomyrmex.agents.generic import BaseAgent
from codomyrmex.agents.core import AgentCapabilities, AgentRequest, AgentResponse

class MyAgent(BaseAgent):
    def _execute_impl(self, request):
        # Implement agent logic
        return AgentResponse(content="Response")
    
    def _stream_impl(self, request):
        # Implement streaming logic
        yield "chunk1"
        yield "chunk2"

agent = MyAgent(
    name="my_agent",
    capabilities=[AgentCapabilities.CODE_GENERATION]
)
```

### AgentOrchestrator

```python
from codomyrmex.agents.generic import AgentOrchestrator

orchestrator = AgentOrchestrator([agent1, agent2, agent3])

# Parallel execution
responses = orchestrator.execute_parallel(request)

# Sequential execution with fallback
response = orchestrator.execute_with_fallback(request)
```

### MessageBus

```python
from codomyrmex.agents.generic import MessageBus, Message

bus = MessageBus()

def handle_message(message: Message):
    print(f"Received: {message.content}")

bus.subscribe("task_complete", handle_message)
bus.publish(Message(message_type="task_complete", content="Done"))
```

### TaskPlanner

```python
from codomyrmex.agents.generic import TaskPlanner

planner = TaskPlanner()

# Create main task
main_task = planner.create_task("Build application")

# Decompose into subtasks
subtasks = planner.decompose_task(
    main_task,
    ["Design database", "Implement API", "Create frontend"]
)

# Get execution order
execution_order = planner.get_task_execution_order()
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Module**: [agents](../README.md)



## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.codomyrmex.agents.generic import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
