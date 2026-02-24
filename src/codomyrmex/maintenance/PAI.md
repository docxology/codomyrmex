# Personal AI Infrastructure — Maintenance Module

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Maintenance module provides automated codebase health management — health checks,
scheduled maintenance tasks, RASP documentation auditing, stale dependency detection,
and automated cleanup operations. For PAI, it is the primary tool for keeping the
codomyrmex toolbox in a known-good state before and after Algorithm runs.

The two MCP tools (`maintenance_health_check` and `maintenance_list_tasks`) allow PAI
agents to trigger health verifications and inspect maintenance state without requiring
Python imports or trust-escalation.

## PAI Capabilities

### Health Checking

Run named health checks that return structured pass/fail status:

```python
from codomyrmex.maintenance.health.health_check import (
    HealthChecker, HealthCheck, HealthStatus
)

checker = HealthChecker()
checker.register(HealthCheck(
    name="mcp_bridge",
    description="MCP bridge reachable",
    check_fn=lambda: (HealthStatus.HEALTHY, "Bridge responding", {}),
))
result = checker.run("mcp_bridge")
# result.status: HealthStatus.HEALTHY | DEGRADED | UNHEALTHY
# result.message: str
# result.duration_ms: float
```

### Maintenance Task Scheduling

Register and schedule recurring maintenance operations:

```python
from codomyrmex.maintenance.health.scheduler import MaintenanceScheduler

scheduler = MaintenanceScheduler()
scheduler.register_task(
    name="rasp_audit",
    fn=lambda: audit_rasp_docs(),
    interval_hours=24,
)
scheduler.run_all()
```

### RASP Documentation Auditing

Verify that all modules have the required RASP documentation files
(`README.md`, `AGENTS.md`, `SPEC.md`, `PAI.md`):

```python
from codomyrmex.maintenance import audit_rasp_compliance

results = audit_rasp_compliance()
# Returns per-module compliance status with missing file lists
```

### Stale Dependency Detection

```python
from codomyrmex.maintenance import check_dependency_freshness

report = check_dependency_freshness()
# Returns packages with newer versions available
```

## MCP Tools

The following tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.maintenance_health_check` | Run a named health check and return its status | Safe | maintenance |
| `codomyrmex.maintenance_list_tasks` | List all registered maintenance tasks and their status | Safe | maintenance |

### MCP Tool Usage Examples

**Run a health check:**
```python
# Via MCP (agent-facing)
result = mcp_call("codomyrmex.maintenance_health_check", {
    "name": "mcp_bridge",
    "check_fn_source": "default"
})
# Returns:
# {
#   "status": "ok",
#   "check_name": "mcp_bridge",
#   "health_status": "healthy",
#   "message": "System operational",
#   "duration_ms": 1.2
# }
```

**List maintenance tasks:**
```python
result = mcp_call("codomyrmex.maintenance_list_tasks")
# Returns:
# {
#   "status": "ok",
#   "task_count": N,
#   "tasks": [{"name": "rasp_audit", "last_run": "...", "status": "..."}]
# }
```

## PAI Algorithm Phase Mapping

| Phase | Maintenance Contribution | Key Functions |
|-------|--------------------------|---------------|
| **OBSERVE** (1/7) | Audit RASP compliance; verify module health before work begins | `audit_rasp_compliance()`, `HealthChecker.run()` |
| **PLAN** (3/7) | Identify which modules have degraded health before targeting them | `maintenance_health_check` MCP tool |
| **VERIFY** (6/7) | Confirm documentation coverage and dependency freshness post-change | `check_dependency_freshness()`, `audit_rasp_compliance()` |
| **LEARN** (7/7) | Track maintenance metrics over time; schedule follow-up tasks | `MaintenanceScheduler`, health trend logging |

### Concrete PAI Usage Pattern

PAI OBSERVE phase can call `maintenance_health_check` to gate risky operations:

```python
# PAI OBSERVE — confirm codomyrmex is healthy before running destructive tools
result = mcp_call("codomyrmex.maintenance_health_check", {"name": "system"})
if result["health_status"] != "healthy":
    # ISC: System health confirmed before destructive operations → FAIL
    raise RuntimeError(f"System unhealthy: {result['message']}")
```

## PAI Configuration

| Environment Variable | Default | Purpose |
|---------------------|---------|---------|
| `CODOMYRMEX_MAINTENANCE_LOG_DIR` | `logs/maintenance/` | Where maintenance logs are written |
| `CODOMYRMEX_HEALTH_TIMEOUT_MS` | `5000` | Health check timeout in milliseconds |

## PAI Best Practices

1. **Run health checks at OBSERVE, not after BUILD**: Catching a degraded module before
   investing in BUILD saves time. Call `maintenance_health_check` in OBSERVE when the
   task touches integration points (MCP, events, trust gateway).

2. **RASP audit as VERIFY criterion**: For tasks that add or modify modules, include
   an ISC criterion like "All modified modules pass RASP compliance audit" and verify
   it with `audit_rasp_compliance()`.

3. **Don't schedule maintenance tasks inside Algorithm runs**: The `MaintenanceScheduler`
   is for background processes. Inside a PAI session, use the MCP tools directly rather
   than setting up persistent schedulers that outlive the session.

## Architecture Role

**Platform Layer** — Consumes `documentation/` (doc audits), `static_analysis/` (code
analysis), `system_discovery/` (module listing). Provides automated maintenance for the
entire project.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
