# Orchestrator Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Workflow execution and scheduling orchestrator. Provides workflow dependency analysis, scheduler metrics, and execution engine for multi-step task automation.

## Configuration Options

The orchestrator module operates with sensible defaults and does not require environment variable configuration. Workflow definitions use YAML or programmatic construction. Scheduler concurrency and retry policies are configurable.

## MCP Tools

This module exposes 2 MCP tool(s):

- `get_scheduler_metrics`
- `analyze_workflow_dependencies`

## PAI Integration

PAI agents invoke orchestrator tools through the MCP bridge. Workflow definitions use YAML or programmatic construction. Scheduler concurrency and retry policies are configurable.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep orchestrator

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/orchestrator/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
