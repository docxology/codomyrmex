# Personal AI Infrastructure — Collaboration Module

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Collaboration module provides multi-agent and multi-user collaboration primitives —
swarm execution, shared workspaces, real-time synchronization, and collaborative editing
interfaces for team-based AI-assisted development.

For PAI, it is the backbone of **agent teams**: when the Algorithm decides to parallelize
work across N agents, this module's `SwarmManager` and `AgentProxy` objects orchestrate
mission dispatch, result collection, and task decomposition.

It also exposes three MCP tools that allow PAI to submit missions to swarms, query pool
status, and enumerate available agents without any Python imports.

## PAI Capabilities

### Swarm Mission Dispatch

Submit a multi-step mission to a dynamically-configured agent swarm:

```python
from codomyrmex.collaboration.protocols.swarm import SwarmManager, AgentProxy, TaskDecomposer

swarm = SwarmManager()
swarm.add_agent(AgentProxy(name="engineer", role="builder"))
swarm.add_agent(AgentProxy(name="reviewer", role="verifier"))

results = swarm.execute("Implement and review authentication middleware")
# Returns: {"engineer": "...", "reviewer": "..."}

subtasks = TaskDecomposer.decompose("Implement and review authentication middleware")
# Returns: ["Implement middleware", "Write tests", "Review code"]
```

### Task Decomposition

Break compound missions into atomic subtasks for parallel dispatch:

```python
from codomyrmex.collaboration.protocols.swarm import TaskDecomposer

subtasks = TaskDecomposer.decompose("Build auth system with tests and docs")
# Returns ordered list of atomic subtask strings
```

### Protocol Types

The module ships three collaboration protocols selectable per-swarm:

| Protocol | Class | Use Case |
|----------|-------|----------|
| Broadcast | `BroadcastProtocol` | All agents get the same task (diverse perspectives) |
| Capability routing | `CapabilityRoutingProtocol` | Route tasks to agents by declared skill |
| Round-robin | `RoundRobinProtocol` | Distribute tasks evenly across agents |

```python
from codomyrmex.collaboration.protocols import BroadcastProtocol, CapabilityRoutingProtocol

swarm.set_protocol(BroadcastProtocol())
# or
swarm.set_protocol(CapabilityRoutingProtocol({"build": "engineer", "test": "qa"}))
```

## MCP Tools

The following tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.swarm_submit_task` | Submit a mission to the agent swarm for distributed execution | Safe | collaboration |
| `codomyrmex.pool_status` | Return live status of the agent pool | Safe | collaboration |
| `codomyrmex.list_agents` | List all registered agents in the current pool | Safe | collaboration |

### MCP Tool Usage Examples

**Submit a swarm task:**
```python
# Via MCP (agent-facing)
result = mcp_call("codomyrmex.swarm_submit_task", {
    "mission": "Refactor authentication module for async support",
    "agents": [
        {"name": "backend_engineer", "role": "builder"},
        {"name": "security_reviewer", "role": "auditor"}
    ]
})
# Returns: {"mission": "...", "results": {...}, "subtasks": [...], "agent_count": 2}
```

**Query pool status:**
```python
result = mcp_call("codomyrmex.pool_status")
# Returns: {"status": "ok", "agent_count": N, "active_missions": M}
```

**List available agents:**
```python
result = mcp_call("codomyrmex.list_agents")
# Returns: {"status": "ok", "agents": [{"name": "...", "role": "..."}, ...]}
```

## PAI Algorithm Phase Mapping

| Phase | Collaboration Contribution | Key Classes/Functions |
|-------|----------------------------|-----------------------|
| **PLAN** (3/7) | Allocate work across agents; select protocol for the task | `SwarmManager`, `CapabilityRoutingProtocol` |
| **BUILD** (4/7) | Dispatch parallel build tasks to specialized agents | `SwarmManager.execute()`, `AgentProxy` |
| **EXECUTE** (5/7) | Synchronize parallel agent work in shared workspaces; broadcast missions | `BroadcastProtocol`, `RoundRobinProtocol` |
| **VERIFY** (6/7) | Aggregate and reconcile results from parallel agents | `TaskDecomposer`, result merging |

### Concrete PAI Usage Pattern

When the PAI Algorithm reaches PLAN phase with 3+ independent ISC criteria, it may
invoke `swarm_submit_task` to parallelize work:

```python
# PAI PLAN phase decision: parallelize 3 independent ISC criteria
mcp_call("codomyrmex.swarm_submit_task", {
    "mission": "ISC-C1: Authentication JWT tokens valid. ISC-C2: Rate limiting enforced. ISC-C3: Audit log written.",
    "agents": [
        {"name": "auth_impl", "role": "builder"},
        {"name": "rate_impl", "role": "builder"},
        {"name": "audit_impl", "role": "builder"},
    ]
})
```

## PAI Configuration

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `CODOMYRMEX_SWARM_TIMEOUT` | `60` | Seconds before a swarm mission times out |
| `CODOMYRMEX_MAX_AGENTS` | `16` | Maximum agents per swarm pool |

## PAI Best Practices

1. **Match agent roles to ISC domains**: When decomposing via PLAN, assign agent roles
   to ISC domain names (e.g., `"role": "auth"` for auth-domain criteria). This makes
   result attribution unambiguous.

2. **Use BroadcastProtocol for verification**: When multiple agents must cross-check the
   same output (e.g., security + correctness), `BroadcastProtocol` ensures all see the
   same artifact.

3. **Keep missions atomic**: `TaskDecomposer` works best when the mission maps directly
   to 2–8 ISC criteria. Mega-missions with 20+ criteria should be split into child PRDs
   first, then dispatched as separate swarm calls.

## Architecture Role

**Service Layer** — Consumes `concurrency/` (locks), `events/` (sync events),
`git_operations/` (merge resolution). Enables multi-agent parallel work. The 6 optional
cloud SDK failures do not affect this module.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
