# Codomyrmex Agents — src/codomyrmex/logging_monitoring

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Centralized logging and monitoring infrastructure. Standardizes output (JSON/Text) and session-based correlation.

## Active Components

- `SPEC.md` – Functional specification (v0.1.0 Unified Streamline)
- `logger_config.py` – Primary configuration logic
- `json_formatter.py` – Standardized `JSONFormatter` (formerly `JsonFormatter`)
- `audit.py` – Domain-specific auditing
- `rotation.py` – Log file management

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
