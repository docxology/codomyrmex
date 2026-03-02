# Health - Agent Coordination

## Purpose

Health check and maintenance scheduling framework providing a registry of callable checks with aggregated status reporting and a cron-like task scheduler with retry logic.

## Key Components

| Component | Role |
|-----------|------|
| `HealthChecker` | Registry and executor for health check functions |
| `HealthCheck` | Dataclass: name, description, check_fn callable, critical flag, timeout_ms |
| `HealthCheckResult` | Dataclass: name, status, message, duration_ms, details, timestamp |
| `AggregateHealthReport` | Aggregated report: overall_status, per-check results, counts |
| `HealthStatus` | Enum: HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN |
| `MaintenanceScheduler` | Cron-like scheduler with priority, retry logic, and result history |
| `MaintenanceTask` | Dataclass: name, description, action callable, schedule config, priority |
| `ScheduleConfig` | Dataclass: interval_seconds, max_retries, retry_delay, timeout, run_on_startup |
| `TaskResult` | Dataclass: task_name, status, started_at, completed_at, duration, retries_used |
| `TaskPriority` | Enum: LOW, MEDIUM, HIGH, CRITICAL |
| `TaskStatus` | Enum: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED |

## Operating Contracts

- Health check functions must return `tuple[HealthStatus, str, dict]` (status, message, details).
- Checks marked `critical=True` cause overall status to be UNHEALTHY on failure.
- Scheduler `execute()` retries up to `max_retries` times with `retry_delay_seconds` between attempts.
- `get_due_tasks(now)` returns tasks sorted by priority whose interval has elapsed since last run.

## Integration Points

- **Parent module**: `maintenance/` exposes `maintenance_health_check` and `maintenance_list_tasks` MCP tools.
- **Used by**: `system_discovery/` health monitoring.

## Navigation

- **Parent**: [maintenance/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
