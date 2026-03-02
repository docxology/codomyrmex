# Codomyrmex Agents — src/codomyrmex/collaboration/swarm

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Implements a complete swarm orchestration layer with role-based agents (`SwarmAgent`), typed messages (`SwarmMessage`), a topic-routed message bus (`MessageBus`), capability-based agent pooling (`AgentPool`), DAG task decomposition (`TaskDecomposer`), and configurable consensus strategies (`ConsensusEngine`). Designed for complex multi-agent workflows with dependency ordering and load balancing.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `protocol.py` | `AgentRole` | Enum: CODER, REVIEWER, ARCHITECT, TESTER, DOCUMENTER, DEVOPS |
| `protocol.py` | `MessageType` | Enum: TASK_ASSIGNMENT, REVIEW_REQUEST, APPROVAL_VOTE, STATUS_UPDATE, RESULT, ERROR |
| `protocol.py` | `TaskStatus` | Enum: PENDING, ASSIGNED, IN_PROGRESS, REVIEW, APPROVED, REJECTED, COMPLETED, FAILED |
| `protocol.py` | `SwarmMessage` | Typed message with sender, recipient, payload, and auto-generated ID |
| `protocol.py` | `SwarmAgent` | Agent with role, capabilities set, load tracking, and availability check |
| `protocol.py` | `TaskAssignment` | Task descriptor with required role, capabilities, status, and priority |
| `pool.py` | `AgentPool` | Registers agents, assigns tasks by role+capability+load, releases slots |
| `pool.py` | `AssignmentError` | Raised when no suitable agent is available |
| `message_bus.py` | `MessageBus` | Topic-routed pub/sub with wildcard matching (`*` single, `#` multi-segment) |
| `message_bus.py` | `Subscription` | Binds subscriber ID, topic pattern, and handler callback |
| `decomposer.py` | `TaskDecomposer` | Keyword-heuristic decomposition into role-based `SubTask` DAG |
| `decomposer.py` | `SubTask` | Decomposed sub-task with dependency edges and priority |
| `decomposer.py` | `CyclicDependencyError` | Raised on cycle detection during topological sort |
| `consensus.py` | `ConsensusEngine` | Resolves votes via majority, weighted, or veto strategies |
| `consensus.py` | `Vote` | Agent vote with boolean approval, weight, and reason |
| `consensus.py` | `ConsensusResult` | Decision outcome with approval score and strategy used |
| `consensus.py` | `Decision` | Enum: APPROVED, REJECTED, DEADLOCK, VETOED |

## Operating Contracts

- `AgentPool.assign()` raises `AssignmentError` when no agent matches required role and capabilities.
- `AgentPool.release()` must be called when a task completes to free the agent's slot.
- `MessageBus` supports `*` (single-segment) and `#` (multi-segment) wildcard patterns for topic matching.
- `TaskDecomposer.execution_order()` uses Kahn's algorithm and raises `CyclicDependencyError` on cycles.
- `ConsensusEngine.resolve()` returns `Decision.DEADLOCK` on empty vote lists.
- `SwarmAgent.available` is `True` only when `active_tasks < max_concurrent`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (get_logger)
- **Used by**: `collaboration.mcp_tools` (MCP tool surface), higher-level orchestration

## Navigation

- **Parent**: [collaboration](../README.md)
- **Root**: [Root](../../../../README.md)
