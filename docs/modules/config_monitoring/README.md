# Config Monitoring Module

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: May 2026

## Overview

`codomyrmex.config_monitoring` tracks configuration changes over time. It supports file hashing, change records, environment snapshots, drift detection, audit history, and watcher-based hot reload workflows.

## Source of Truth

- Source implementation: [../../../src/codomyrmex/config_monitoring/](../../../src/codomyrmex/config_monitoring/)
- Source README: [../../../src/codomyrmex/config_monitoring/README.md](../../../src/codomyrmex/config_monitoring/README.md)
- Source SPEC: [../../../src/codomyrmex/config_monitoring/SPEC.md](../../../src/codomyrmex/config_monitoring/SPEC.md)
- Source AGENTS: [../../../src/codomyrmex/config_monitoring/AGENTS.md](../../../src/codomyrmex/config_monitoring/AGENTS.md)

## Operating Notes

- Keep hashing deterministic and stream large files safely.
- Stop watchers cleanly; avoid unbounded background threads.
- Treat snapshot and audit files as local operational state, not source-controlled deliverables.
- Validate path containment before scanning or writing monitoring state.

## Navigation

- **Parent Directory**: [modules](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
