# Codomyrmex Fabric Integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Codomyrmex `fabric` module integrates the [danielmiessler/fabric](https://github.com/danielmiessler/fabric) pattern-based AI workflow framework into the broader Codomyrmex ecosystem.

It provides configuration management, subprocess execution wrapping, and orchestration logic to apply complex analytical patterns to any workflow payload.

## Core Features

- **Pattern Management**: Seamlessly execute `fabric` patterns using local or remote models.
- **Workflow Orchestration**: Chain patterns for comprehensive reports (e.g., Code Analysis → Optimization → Documentation).
- **Graceful Degradation**: If `fabric` is not installed on the system, the integration fails gracefully to ensure the parent Codomyrmex agent encounters no hard crashes.
- **Zero-Mock Testing**: All implementations follow the Codomyrmex Zero-Mock philosophy. We invoke real `fabric` tools or capture real degraded state.

## Directory Contents

- `PAI.md` – Personal AI infrastructure operational notes
- `AGENTS.md` – Navigation and coordination protocols
- `SPEC.md` – Technical capabilities mapping
- `__init__.py` – Exports for the Fabric API
- `fabric_config_manager.py` – Reads/writes Fabric configuration to disk
- `fabric_manager.py` – Core execution bounds and subprocess monitoring
- `fabric_orchestrator.py` – Multistep pattern chaining abstractions

## System Requirement

`fabric` must be locally executable to leverage the full functionality of this module. A valid API Key (e.g. OpenAI) should be bound.

## Navigation

- **Parent Directory**: [llm](../README.md)
- **Project Root**: ../../../../README.md
