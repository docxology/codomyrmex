# Codomyrmex Agents — src/codomyrmex/agents/openclaw

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

OpenClaw agent integration providing autonomous AI assistance with multi-channel messaging, Gateway control plane management, and LLM-agnostic agent invocation.

## Active Components

- `PAI.md` – AI context document
- `README.md` – Human documentation
- `SPEC.md` – Functional specification
- `__init__.py` – Module exports
- `openclaw_client.py` – CLI client extending CLIAgentBase
- `openclaw_integration.py` – Integration adapter for Codomyrmex modules
- `py.typed` – PEP 561 type marker

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update task queues when necessary.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Project Root**: ../../../../README.md - Main project documentation
