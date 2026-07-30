# ml_pipeline — PAI Integration

**Version**: v1.3.0 | **Status**: Experimental | **Last Updated**: July 2026

## AI Capabilities

The `ml_pipeline` module exposes two stateless receipt-producing functions to
Python and MCP callers. It does not orchestrate, execute, persist, monitor, or
authorize ML workloads.

## Algorithm Phase Mapping

| PAI Phase | Relevance | Description |
| :--- | :--- | :--- |
| **BUILD** (4/7) | Limited | Echo a caller-supplied pipeline name and step list |
| **EXECUTE** (5/7) | Naming only | Return an execution-shaped echo receipt; no actuation |
| **VERIFY** (6/7) | None | No validation or output verification is implemented |
| **LEARN** (7/7) | None | No metrics, state, or learning loop is implemented |

## MCP Tools

| Tool | Category | Trust | Description |
| :--- | :--- | :--- | :--- |
| `ml_pipeline_create` | Receipt | Non-actuating | Echo a name and ordered step descriptors |
| `ml_pipeline_execute` | Receipt | Non-actuating | Echo a name and input mapping as outputs |

## Agent Role Access

| Agent Role | Access Level | Permitted Operations |
| :--- | :--- | :--- |
The module implements no role-based access control. Any role restrictions must
be applied by the caller or an enclosing authorization layer.

## Signposting

- **Self**: [PAI.md](PAI.md) — This document
- **Parent**: [README.md](README.md) — Module overview
- **Siblings**:
  - [AGENTS.md](AGENTS.md) — Agent coordination
  - [SPEC.md](SPEC.md) — Functional specification
- **Root Bridge**: [/PAI.md](../../../PAI.md) — PAI system bridge
