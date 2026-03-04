# Operating System Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

OS-level utilities for Linux, macOS, and Windows. Provides platform-specific operations, process management, and system information gathering.

## Configuration Options

The operating_system module operates with sensible defaults and does not require environment variable configuration. Platform detection is automatic. OS-specific modules load conditionally based on the detected operating system.

## PAI Integration

PAI agents interact with operating_system through direct Python imports. Platform detection is automatic. OS-specific modules load conditionally based on the detected operating system.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep operating_system

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/operating_system/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
