# Collaboration - API Specification

## Introduction

The Collaboration module provides typed multi-agent collaboration primitives, including swarm management, task decomposition, message routing, and consensus.

## Endpoints / Functions / Interfaces

### Class: `SwarmManager`

- **Description**: Manages a swarm of collaborating agents.
- **Constructor**:
    - No arguments. Register concrete `SwarmAgent` instances after construction.
- **Methods**:

#### `register_agent(agent: SwarmAgent) -> None`

- **Description**: Register a typed agent and subscribe it to result messages.

#### `queue_mission(mission: str) -> list[dict[str, Any]]`

- **Description**: Decompose a mission and return its queued task records without waiting for execution.

#### `execute_mission(mission: str) -> list[dict[str, Any]]`

- **Description**: Decompose and execute a mission asynchronously, returning each task result.

#### `request_consensus(proposal: str, votes: list[SwarmVote], strategy: str = "majority") -> ConsensusResult`

- **Description**: Resolve and publish a swarm consensus decision.

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

### Class: `SwarmAgent`

- **Description**: Typed swarm participant with an ID, role, capabilities, and concurrency limit.
- **Constructor**: `SwarmAgent(agent_id: str, role: AgentRole, capabilities: set[str] = set(), max_concurrent: int = 3)`

### Class: `TaskDecomposer`

- **Description**: Decomposes complex tasks into subtasks for parallel execution.
- **Constructor**:
    - `strategy` (str, optional): Decomposition strategy ("hierarchical", "functional", "parallel"). Default: "hierarchical".
- **Methods**:

#### `decompose(task: str) -> list[SubTask]`

- **Description**: Decompose a task into subtasks.
- **Parameters/Arguments**:
    - `task` (str): Mission description to decompose.
- **Returns**:
    - `list[SubTask]`: Ordered role-based subtasks.

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
