# Codomyrmex Agents — src/codomyrmex/security/ai_safety

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

AI safety components for prompt injection defense, jailbreak detection, and adversarial input containment. Provides a unified AISafetyMonitor that wraps optional defense module integrations (ActiveDefense, RabbitHole) into a single monitoring interface.

## Active Components

- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file (AISafetyMonitor class; optional ActiveDefense and RabbitHole integration)

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links

- **Parent Directory**: [security](../README.md)
- **Project Root**: ../../../../README.md
