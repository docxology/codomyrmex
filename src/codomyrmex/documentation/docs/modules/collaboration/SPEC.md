# Collaboration -- Technical Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Functional Requirements

### FR-1: Multi-Agent Communication
- Message passing via MessageBus with typed SwarmMessage and SwarmMessageType.
- Channel-based communication with broadcasting and direct messaging.

### FR-2: Task Coordination
- TaskDecomposer shall break complex tasks into distributable subtasks.
- Task management with priority, status tracking, and dependency resolution.

### FR-3: Consensus
- ConsensusProtocol shall support voting-based decision making.
- Leader election for coordinator selection.

### FR-4: Swarm Management
- SwarmManager shall orchestrate agent pools with role-based assignment.
- AgentPool shall support dynamic agent registration and status tracking.

## Navigation

- **Source**: [src/codomyrmex/collaboration/](../../../../src/codomyrmex/collaboration/)
- **Extended README**: [README.md](readme.md)
- **AGENTS**: [AGENTS.md](AGENTS.md)
- **Parent**: [All Modules](../README.md)
