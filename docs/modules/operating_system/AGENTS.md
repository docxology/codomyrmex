# Operating System -- Agent Coordination

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides cross-platform operating system abstraction with auto-detection and platform-specific providers for macOS, Linux, and Windows. Offers unified APIs for system info, process management, disk usage, service listing, network interfaces, and command execution.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `os_system_info` | Retrieve system information for the current platform | Standard | operating_system |
| `os_list_processes` | List running processes on the current platform | Standard | operating_system |
| `os_disk_usage` | Return disk usage for all mounted filesystems | Standard | operating_system |
| `os_network_info` | Return network interface information | Standard | operating_system |
| `os_execute_command` | Execute a shell command on the current platform | Trusted | operating_system |
| `os_environment_variables` | Return current environment variables with optional prefix filter | Standard | operating_system |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| OBSERVE | Infrastructure Agent | Gather system information and monitor resource usage |
| EXECUTE | Infrastructure Agent | Execute commands and manage system resources |


## Agent Instructions

1. os_execute_command has a 30-second default timeout; adjust for long-running commands
2. os_environment_variables accepts an optional prefix filter to narrow results
3. Platform auto-detection dispatches to macOS, Linux, or Windows provider


## Navigation

- [Source README](../../src/codomyrmex/operating_system/README.md) | [SPEC.md](SPEC.md)
