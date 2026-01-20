# Codomyrmex Agents — src/codomyrmex/events

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Orchestrates the asynchronous event-driven architecture. Standardizes emission and subscription patterns across the platform.

## Active Components

- `SPEC.md` – Functional specification (v0.1.0 Unified Streamline)
- `event_bus.py` – Core routing logic
- `event_emitter.py` – Emission interface
- `event_listener.py` – Subscription manager (legacy `unregister`/`listeners` removed)
- `event_logger.py` – Telemetry and auditing
- `event_schema.py` – Data structure definitions

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
