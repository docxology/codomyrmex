# Workflow Execution Scripts

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Workflow execution utilities for running defined workflow files with optional dry-run support, providing a CLI interface to the codomyrmex orchestration engine.

## Purpose

These scripts provide a command-line runner for workflow definition files, supporting dry-run validation, step-by-step execution, and subprocess orchestration of multi-step workflows.

## Contents

| File | Description |
|------|-------------|
| `workflow_runner.py` | CLI workflow executor with `--dry-run` support for workflow definition files |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
# Execute a workflow
uv run python scripts/workflow_execution/workflow_runner.py workflow.json

# Dry run (validate without executing)
uv run python scripts/workflow_execution/workflow_runner.py workflow.json --dry-run
```

## Agent Usage

Agents orchestrating multi-step tasks should use `workflow_runner.py` with `--dry-run` first to validate workflow definitions before execution. The runner integrates with the codomyrmex orchestrator module.

## Related Module

- Source: `src/codomyrmex/orchestrator/`
- MCP Tools: `get_scheduler_metrics`, `analyze_workflow_dependencies`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
