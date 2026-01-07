# Codomyrmex Agents — src/codomyrmex/agents/generic

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Base agent classes and utilities. Provides abstract base classes for all agents, agent orchestration, message bus for inter-agent communication, and task planning capabilities. Serves as the foundation for all agent implementations.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `agent_orchestrator.py` – Agent orchestration and coordination
- `base_agent.py` – Base agent class implementation
- `message_bus.py` – Message bus for inter-agent communication
- `task_planner.py` – Task planning utilities

## Key Classes and Functions

### BaseAgent (`base_agent.py`)
- `BaseAgent(name: str, capabilities: list[AgentCapabilities], config: Optional[dict] = None)` – Base agent class (implements AgentInterface)
- `execute(request: AgentRequest) -> AgentResponse` – Execute an agent request
- `stream(request: AgentRequest) -> Iterator[str]` – Stream response
- `get_capabilities() -> list[AgentCapabilities]` – Get supported capabilities
- `validate_request(request: AgentRequest) -> list[str]` – Validate request

### AgentOrchestrator (`agent_orchestrator.py`)
- `AgentOrchestrator()` – Orchestrate multiple agents
- `coordinate_agents(agents: list[BaseAgent], request: AgentRequest) -> AgentResponse` – Coordinate multiple agents

### MessageBus (`message_bus.py`)
- `MessageBus()` – Message bus for inter-agent communication
- `publish(message: AgentMessage) -> None` – Publish message
- `subscribe(agent: BaseAgent, message_type: str) -> None` – Subscribe agent to message type

### TaskPlanner (`task_planner.py`)
- `TaskPlanner()` – Task planning utilities
- `plan_task(goal: str, context: dict) -> TaskPlan` – Create task plan

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [agents](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation