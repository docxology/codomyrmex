# Config Monitoring API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: April 2026

## Purpose

This document describes the public Python and MCP interfaces for `codomyrmex.config_monitoring`.

## Python API

| Symbol | Type | Purpose |
|:---|:---|:---|
| `ConfigurationMonitor` | Class | Detects configuration changes, stores snapshots, and summarizes monitoring state |
| `ConfigWatcher` | Class | Polls a configuration file and invokes a callback when it changes |
| `ConfigChange` | Dataclass | Describes a detected created, modified, or deleted configuration file |
| `ConfigSnapshot` | Dataclass | Stores file hashes for an environment snapshot |
| `ConfigAudit` | Dataclass | Stores audit results, issues, and recommendations |
| `monitor_config_changes` | Function | Convenience wrapper for monitoring a list of config paths |

## MCP Tools

| Tool | Parameters | Returns |
|:---|:---|:---|
| `config_monitoring_detect_changes` | `config_paths: list[str]`, `workspace_dir: str | None` | Status, checked path count, detected changes, and per-change details |
| `config_monitoring_summary` | `workspace_dir: str | None` | Status and aggregate monitoring summary |
| `config_monitoring_hash_file` | `file_path: str` | Status, file path, and SHA-256 hash |

## Error Shape

MCP tools return dictionaries with `status: "error"` and `message` when an operation fails. Successful calls return `status: "success"` plus tool-specific fields.

## Navigation

- **Module README**: [README.md](README.md)
- **Module SPEC**: [SPEC.md](SPEC.md)
- **Agent guidance**: [AGENTS.md](AGENTS.md)
- **PAI notes**: [PAI.md](PAI.md)
