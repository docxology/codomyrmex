# Collaboration - API Specification

## Introduction

The Collaboration module provides tools for multi-agent collaboration, including swarm management, agent proxies, and task decomposition for coordinated work across multiple AI agents.

## Endpoints / Functions / Interfaces

### Class: `SwarmManager`

- **Description**: Manages a swarm of collaborating agents.
- **Constructor**:
    - `max_agents` (int, optional): Maximum concurrent agents. Default: 10.
    - `coordination_strategy` (str, optional): Strategy for coordination ("round_robin", "priority", "capability"). Default: "round_robin".
- **Methods**:

#### `add_agent(agent: AgentProxy) -> str`

- **Description**: Add an agent to the swarm.
- **Parameters/Arguments**:
    - `agent` (AgentProxy): Agent to add.
- **Returns**:
    - `str`: Agent ID in the swarm.

#### `remove_agent(agent_id: str) -> bool`

- **Description**: Remove an agent from the swarm.
- **Parameters/Arguments**:
    - `agent_id` (str): ID of the agent to remove.
- **Returns**:
    - `bool`: True if removal was successful.

#### `submit_task(task: Task) -> TaskHandle`

- **Description**: Submit a task to the swarm for execution.
- **Parameters/Arguments**:
    - `task` (Task): Task to execute.
- **Returns**:
    - `TaskHandle`: Handle for tracking task progress.

#### `get_status() -> SwarmStatus`

- **Description**: Get current swarm status.
- **Returns**:
    - `SwarmStatus`: Current swarm status.

#### `coordinate(tasks: list[Task]) -> CoordinationResult`

- **Description**: Coordinate multiple tasks across agents.
- **Parameters/Arguments**:
    - `tasks` (list[Task]): Tasks to coordinate.
- **Returns**:
    - `CoordinationResult`: Coordination outcome.

### Class: `AgentProxy`

- **Description**: Proxy for communicating with an AI agent.
- **Constructor**:
    - `agent_id` (str): Unique agent identifier.
    - `capabilities` (list[str]): Agent capabilities.
    - `endpoint` (str, optional): Agent communication endpoint.
- **Methods**:

#### `execute(task: Task) -> TaskResult`

- **Description**: Execute a task on the agent.
- **Parameters/Arguments**:
    - `task` (Task): Task to execute.
- **Returns**:
    - `TaskResult`: Task execution result.

#### `get_capabilities() -> list[str]`

- **Description**: Get agent capabilities.
- **Returns**:
    - `list[str]`: List of capabilities.

#### `get_status() -> AgentStatus`

- **Description**: Get agent status.
- **Returns**:
    - `AgentStatus`: Current agent status.

#### `send_message(message: Message) -> Response`

- **Description**: Send a message to the agent.
- **Parameters/Arguments**:
    - `message` (Message): Message to send.
- **Returns**:
    - `Response`: Agent response.

### Class: `TaskDecomposer`

- **Description**: Decomposes complex tasks into subtasks for parallel execution.
- **Constructor**:
    - `strategy` (str, optional): Decomposition strategy ("hierarchical", "functional", "parallel"). Default: "hierarchical".
- **Methods**:

#### `decompose(task: Task) -> list[Task]`

- **Description**: Decompose a task into subtasks.
- **Parameters/Arguments**:
    - `task` (Task): Task to decompose.
- **Returns**:
    - `list[Task]`: List of subtasks.

#### `merge_results(results: list[TaskResult]) -> TaskResult`

- **Description**: Merge subtask results into a single result.
- **Parameters/Arguments**:
    - `results` (list[TaskResult]): Subtask results.
- **Returns**:
    - `TaskResult`: Merged result.

## Data Models

### Model: `Task`
- `id` (str): Unique task identifier.
- `name` (str): Task name.
- `description` (str): Task description.
- `required_capabilities` (list[str]): Required agent capabilities.
- `priority` (int): Task priority (1-10).
- `dependencies` (list[str]): IDs of tasks this depends on.
- `metadata` (dict): Additional metadata.

### Model: `TaskResult`
- `task_id` (str): Task identifier.
- `success` (bool): Whether task succeeded.
- `output` (Any): Task output.
- `error` (str | None): Error message if failed.
- `duration` (float): Execution duration in seconds.
- `agent_id` (str): Agent that executed the task.

### Model: `SwarmStatus`
- `total_agents` (int): Total agents in swarm.
- `active_agents` (int): Currently active agents.
- `pending_tasks` (int): Tasks waiting for execution.
- `running_tasks` (int): Currently executing tasks.
- `completed_tasks` (int): Completed tasks.

### Model: `AgentStatus`
- `agent_id` (str): Agent identifier.
- `status` (str): Status (idle, busy, offline).
- `current_task` (str | None): Current task ID.
- `capabilities` (list[str]): Agent capabilities.

## Authentication & Authorization

Agent communication may require authentication. Configure appropriate credentials for agent endpoints.

## Rate Limiting

N/A - Task submission may be subject to swarm capacity limits.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
