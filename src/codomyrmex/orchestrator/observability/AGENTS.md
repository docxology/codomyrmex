# Codomyrmex Agents -- src/codomyrmex/orchestrator/observability

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides orchestrator observability through typed event factories for workflow and task lifecycle transitions, plus reporting utilities for run summaries, individual script logs, and auto-generated script documentation.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `orchestrator_events.py` | `workflow_started` | Factory producing `WORKFLOW_STARTED` Event with total task count |
| `orchestrator_events.py` | `workflow_completed` | Factory producing `WORKFLOW_COMPLETED` Event with pass/fail/skip counts and elapsed time |
| `orchestrator_events.py` | `workflow_failed` | Factory producing `WORKFLOW_FAILED` Event (priority 2) |
| `orchestrator_events.py` | `task_started` | Factory producing `TASK_STARTED` Event |
| `orchestrator_events.py` | `task_completed` | Factory producing `TASK_COMPLETED` Event with execution time and attempt count |
| `orchestrator_events.py` | `task_failed` | Factory producing `TASK_FAILED` Event (priority 2) |
| `orchestrator_events.py` | `task_retrying` | Factory producing `TASK_RETRYING` Event with attempt, delay, and error info |
| `reporting.py` | `save_log` | Writes individual script execution logs (stdout, stderr, errors) to disk |
| `reporting.py` | `generate_report` | Aggregates results into a JSON summary report grouped by subdirectory |
| `reporting.py` | `generate_script_documentation` | Auto-generates Markdown documentation for discovered scripts via `--help` |

## Operating Contracts

- All event factory functions return `Event` instances from `codomyrmex.events.core.event_schema`; they do not emit events themselves.
- Events set `source` to `orchestrator.{workflow_name}` for consistent filtering.
- Failure events (`workflow_failed`, `task_failed`) use priority 2 for elevated handling.
- `save_log` creates directories as needed and handles bytes-to-string decoding for stdout/stderr.
- `generate_report` logs a `RUN_SUMMARY` event through the module logger.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.events.core.event_schema` (Event, EventType), `codomyrmex.logging_monitoring`, `codomyrmex.utils.cli_helpers`, `orchestrator.discovery`
- **Used by**: `orchestrator.process_orchestrator`, any workflow runner that needs structured event reporting

## Navigation

- **Parent**: [orchestrator](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
