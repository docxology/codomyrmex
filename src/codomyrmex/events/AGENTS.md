# Codomyrmex Agents — src/codomyrmex/events

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026 (Sprint 34)

## Purpose
Typed event bus with emitter patterns, notification systems, and integration bus for cross-module communication. Sprint 34 adds **P2P agent mailboxes** (`send_to_agent`, `receive`, `drain_inbox`) backed by optional **EventStore** durability (`replay_from_store`), plus `events_send_to_agent` and `events_agent_inbox` MCP tools.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `core/` – Core abstractions and base classes
- `dead_letter.py` – Internal implementation module
- `emitters/` – emitters module implementation
- `event_store.py` – Internal implementation module
- `handlers/` – Request/event handlers
- `integration_bus.py` – Internal implementation module
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `notification/` – notification module implementation
- `projections.py` – Projections implementation
- `py.typed` – PEP 561 marker for typed package
- `replay.py` – Replay implementation
- `replayer.py` – Replayer implementation
- `streaming/` – streaming module implementation


## Key Interfaces

- `typed_event_bus.py` — Type-safe event publishing and subscription
- `emitters/event_emitter.py` — Event emission with filtering
- `integration_bus.py` — Cross-module event routing + **P2P agent mailbox** (Sprint 34)
  - `send_to_agent(agent_id, message, source)` → posts to in-memory mailbox + optional EventStore
  - `receive(agent_id, timeout)` → FIFO pop with polling
  - `drain_inbox(agent_id)` → atomic drain of all pending messages
  - `replay_from_store(agent_id)` → replay from durable EventStore (requires `event_store=` init arg)
- `event_store.py` — `EventStore` append-only stream with `get_event_store()` module singleton
- `notification/` — Alert and notification systems
- `mcp_tools.py` — `events_send_to_agent` + `events_agent_inbox` MCP tools (Sprint 34)

## Agent Workflow Guidance (Sprint 34)
- Set `IntegrationBus(event_store=EventStore())` for crash-durable P2P mailboxes; use `replay_from_store(agent_id)` to recover after restart.
- Use `events_send_to_agent(agent_id, message)` from any MCP-capable agent to enqueue a task for a peer.
- Use `events_agent_inbox(agent_id, mode="drain")` to atomically collect all pending work.
- Use `events_agent_inbox(agent_id, mode="peek")` for non-destructive monitoring of queue depth.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `dead_letter.py`
- `event_store.py`
- `integration_bus.py`
- `mcp_tools.py`
- `projections.py`
- `py.typed`
- `replay.py`
- `replayer.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
