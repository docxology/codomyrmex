# Containerization - MCP Tool Specification

This document outlines the specification for tools within the Containerization module that are integrated with the Model Context Protocol (MCP). These tools are defined in `mcp_tools.py` and exposed via the `@mcp_tool` decorator.

---

## Tool: `container_runtime_status`

### 1. Tool Purpose and Description

Check the availability of container runtimes (Docker, Kubernetes) and related components (registry, security scanner, optimizer) on the current system.

### 2. Invocation Name

`codomyrmex.container_runtime_status`

### 3. Input Schema (Parameters)

No parameters required.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` | `"ok"` |
| `runtimes` | `object` | Availability of each runtime | See below |
| `runtimes.docker` | `boolean` | Docker manager available | `true` |
| `runtimes.kubernetes` | `boolean` | Kubernetes integration available | `false` |
| `runtimes.registry` | `boolean` | Container registry available | `false` |
| `runtimes.security_scanner` | `boolean` | Security scanner available | `false` |
| `runtimes.optimizer` | `boolean` | Image optimizer available | `false` |

### 5. Error Handling

This tool does not raise errors; it always returns runtime availability flags.

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `container_build`

### 1. Tool Purpose and Description

Build a Docker container image from a Dockerfile path with a specified name and tag.

### 2. Invocation Name

`codomyrmex.container_build`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `image_name` | `string` | Yes | Name for the image | `"myapp"` |
| `dockerfile_path` | `string` | No | Path to Dockerfile directory (default: `"."`) | `"./docker"` |
| `tag` | `string` | No | Image tag (default: `"latest"`) | `"v1.0"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `image` | `string` | Full image name with tag | `"myapp:v1.0"` |
| `result` | `any` | Build result from DockerManager | `...` |

### 5. Error Handling

- Returns `{"status": "error", "error": "Docker manager not available"}` if Docker is not installed.
- Returns `{"status": "error", "error": "<message>"}` on build failures.

### 6. Idempotency

- **Idempotent**: No. Rebuilds the image each time.

---

## Tool: `container_list`

### 1. Tool Purpose and Description

List running Docker containers managed by the local Docker daemon.

### 2. Invocation Name

`codomyrmex.container_list`

### 3. Input Schema (Parameters)

No parameters required.

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `containers` | `array` | List of running container objects | `[...]` |

### 5. Error Handling

- Returns `{"status": "error", "error": "Docker manager not available"}` if Docker is not installed.

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `container_security_scan`

### 1. Tool Purpose and Description

Run a security vulnerability scan on a container image using the built-in `ContainerSecurityScanner`.

### 2. Invocation Name

`codomyrmex.container_security_scan`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `image` | `string` | Yes | Container image to scan | `"python:3.11-slim"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | `"ok"` or `"error"` | `"ok"` |
| `image` | `string` | Scanned image name | `"python:3.11-slim"` |
| `scan_result` | `object` | Vulnerability scan results | `{...}` |

### 5. Error Handling

- Returns `{"status": "error", "error": "Security scanner not available"}` if scanner is not installed.

### 6. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
