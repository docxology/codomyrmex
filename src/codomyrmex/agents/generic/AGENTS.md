# Codomyrmex Agents — src/codomyrmex/agents/generic

## Signposting
- **Parent**: [agents](../AGENTS.md)
- **Self**: [Generic Agents](AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Generic submodule providing shared functionality used across all agent implementations. This includes base agent classes, multi-agent orchestration, inter-agent communication, and task planning utilities.

## Function Signatures

### BaseAgent

```python
def __init__(self, name: str, capabilities: list[AgentCapabilities], config: Optional[dict[str, Any]] = None) -> None
```

Initialize base agent.

**Parameters:**
- `name` (str): Agent name
- `capabilities` (list[AgentCapabilities]): List of capabilities
- `config` (Optional[dict[str, Any]]): Agent configuration

**Returns:** None

```python
def _execute_impl(self, request: AgentRequest) -> AgentResponse
```

Implementation-specific execution logic (to be overridden by subclasses).

**Parameters:**
- `request` (AgentRequest): Agent request

**Returns:** `AgentResponse` - Agent response

**Raises:**
- `NotImplementedError`: If not overridden

```python
def _stream_impl(self, request: AgentRequest) -> Iterator[str]
```

Implementation-specific streaming logic (to be overridden by subclasses).

**Parameters:**
- `request` (AgentRequest): Agent request

**Yields:** `str` - Chunks of response content

**Raises:**
- `NotImplementedError`: If not overridden

### AgentOrchestrator

```python
def execute_parallel(self, request: AgentRequest, agents: Optional[list[AgentInterface]] = None) -> list[AgentResponse]
```

Execute request on multiple agents in parallel.

**Parameters:**
- `request` (AgentRequest): Agent request
- `agents` (Optional[list[AgentInterface]]): Agents to use

**Returns:** `list[AgentResponse]` - List of responses

```python
def execute_sequential(self, request: AgentRequest, agents: Optional[list[AgentInterface]] = None, stop_on_success: bool = False) -> list[AgentResponse]
```

Execute request on multiple agents sequentially.

**Parameters:**
- `request` (AgentRequest): Agent request
- `agents` (Optional[list[AgentInterface]]): Agents to use
- `stop_on_success` (bool): Stop after first success

**Returns:** `list[AgentResponse]` - List of responses

```python
def execute_with_fallback(self, request: AgentRequest, agents: Optional[list[AgentInterface]] = None) -> AgentResponse
```

Execute request with fallback to next agent on failure.

**Parameters:**
- `request` (AgentRequest): Agent request
- `agents` (Optional[list[AgentInterface]]): Agents to use

**Returns:** `AgentResponse` - First successful response or last error

```python
def select_agent_by_capability(self, capability: str, agents: Optional[list[AgentInterface]] = None) -> list[AgentInterface]
```

Select agents that support a specific capability.

**Parameters:**
- `capability` (str): Capability name to check
- `agents` (Optional[list[AgentInterface]]): List of agents to check (defaults to all agents)

**Returns:** `list[AgentInterface]` - List of agents that support the capability

### MessageBus

```python
def subscribe(self, message_type: str, handler: Callable[[Message], None]) -> None
```

Subscribe to messages of a specific type.

**Parameters:**
- `message_type` (str): Message type
- `handler` (Callable): Handler function

**Returns:** None

```python
def publish(self, message: Message) -> None
```

Publish a message to all subscribers.

**Parameters:**
- `message` (Message): Message to publish

**Returns:** None

### TaskPlanner

```python
def create_task(self, description: str, dependencies: Optional[list[str]] = None, metadata: Optional[dict[str, Any]] = None) -> Task
```

Create a new task.

**Parameters:**
- `description` (str): Task description
- `dependencies` (Optional[list[str]]): Task dependencies
- `metadata` (Optional[dict]): Task metadata

**Returns:** `Task` - Created task

```python
def decompose_task(self, main_task: Task, subtask_descriptions: list[str]) -> list[Task]
```

Decompose a task into subtasks.

**Parameters:**
- `main_task` (Task): Main task
- `subtask_descriptions` (list[str]): Subtask descriptions

**Returns:** `list[Task]` - Created subtasks

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Parent Module**: [agents](../AGENTS.md)



## Active Components
- `README.md` - Component file.
- `SPEC.md` - Component file.
- `__init__.py` - Component file.
- `agent_orchestrator.py` - Component file.
- `base_agent.py` - Component file.
- `message_bus.py` - Component file.
- `task_planner.py` - Component file.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.
