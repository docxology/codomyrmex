# jules

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Jules CLI integration for Codomyrmex agents. This submodule wraps the `julius` command-line tool, enabling Python-native dispatch of long-running agentic tasks. It supports spawning hundreds of targeted background agent processes via batch swarm orchestration and merging capabilities back in automatically via CLI built-ins.

## Core Components

- **`JulesClient`**: Low-level wrapper for executing Jules commands with backoff retries and streaming support (`execute_jules_command`, `dispatch_swarm`).
- **`JulesSwarmDispatcher`**: High-level orchestrator that parses structured checklists (like `TODO.md`) to dynamically parallelize hundreds of tasks and fire distributed agents.
- **`JulesIntegrationAdapter`**: Bridges the Jules client to standardized Codomyrmex workflows (`ai_code_editing`, `llm`, `coding`).

## Directory Contents

- `AGENTS.md` - Agent integration specification
- `PAI.md` - PAI integration notes
- `SPEC.md` - Module specification
- `__init__.py` - Module entry point
- `jules_client.py` - Jules Client
- `jules_integration.py` - Jules Integration

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: ../../../README.md
