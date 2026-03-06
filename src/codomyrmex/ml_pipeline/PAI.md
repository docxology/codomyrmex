# ml_pipeline — PAI Integration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## AI Capabilities

The `ml_pipeline` module provides machine learning pipeline orchestration for AI agents. It supports pipeline definition, execution, and monitoring.

## Algorithm Phase Mapping

| PAI Phase | Relevance | Description |
| :--- | :--- | :--- |
| **BUILD** (4/7) | Primary | Pipeline construction and configuration |
| **EXECUTE** (5/7) | Primary | Pipeline execution and data flow management |
| **VERIFY** (6/7) | Secondary | Pipeline validation and output verification |
| **LEARN** (7/7) | Secondary | Pipeline metrics and performance tracking |

## MCP Tools

| Tool | Category | Trust | Description |
| :--- | :--- | :--- | :--- |
| `ml_pipeline_list_pipelines` | Discovery | Safe | List available ML pipelines |
| `ml_pipeline_get_status` | Monitoring | Safe | Get pipeline execution status |
| `ml_pipeline_run` | Execution | **Destructive** | Execute an ML pipeline |

## Agent Role Access

| Agent Role | Access Level | Permitted Operations |
| :--- | :--- | :--- |
| Engineer | Full | Pipeline creation, execution, monitoring |
| Architect | Read | Pipeline inspection and design review |
| QATester | Execute | Pipeline testing and validation |

## Signposting

- **Self**: [PAI.md](PAI.md) — This document
- **Parent**: [README.md](README.md) — Module overview
- **Siblings**:
  - [AGENTS.md](AGENTS.md) — Agent coordination
  - [SPEC.md](SPEC.md) — Functional specification
- **Root Bridge**: [/PAI.md](../../../PAI.md) — PAI system bridge
