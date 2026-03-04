# Containerization Configuration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Container management, orchestration, and deployment. Provides Docker build/scan/runtime, Kubernetes management, container registry, and security scanning.

## Configuration Options

The containerization module operates with sensible defaults and does not require environment variable configuration. Requires Docker CLI and daemon for container operations. Kubernetes operations require kubectl configured with cluster access.

## MCP Tools

This module exposes 4 MCP tool(s):

- `container_runtime_status`
- `container_build`
- `container_list`
- `container_security_scan`

## PAI Integration

PAI agents invoke containerization tools through the MCP bridge. Requires Docker CLI and daemon for container operations. Kubernetes operations require kubectl configured with cluster access.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep containerization

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/containerization/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
