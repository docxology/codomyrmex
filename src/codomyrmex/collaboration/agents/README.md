# collaboration/agents

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-agent coordination submodule. Provides agent definitions, lifecycle management, and a registry for collaborative workflows. Defines a hierarchy from abstract agents through collaborative and worker specializations to supervisor agents that orchestrate multi-agent tasks.

## Key Exports

### Base Classes

- **`AbstractAgent`** -- Abstract base class for all agents with lifecycle hooks
- **`CollaborativeAgent`** -- Agent with collaboration capabilities (messaging, task sharing)

### Worker Agents

- **`WorkerAgent`** -- Standard worker agent that executes assigned tasks
- **`SpecializedWorker`** -- Worker with domain-specific capabilities

### Supervisor

- **`SupervisorAgent`** -- Orchestrates and delegates work to worker agents

### Registry

- **`AgentRegistry`** -- Central registry for agent registration, lookup, and lifecycle management
- **`get_registry()`** -- Get the singleton AgentRegistry instance

## Directory Contents

- `__init__.py` - Package init; re-exports all agent classes and registry
- `base.py` - AbstractAgent and CollaborativeAgent base classes
- `worker.py` - WorkerAgent and SpecializedWorker implementations
- `supervisor.py` - SupervisorAgent implementation
- `registry.py` - AgentRegistry and singleton accessor
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [collaboration](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
