---
id: build-synthesis-mcp-tool-specification
title: Build Synthesis - MCP Tool Specification
sidebar_label: MCP Tool Specification
---

# Build Synthesis - MCP Tool Specification

## Tool: `build.start_module_build`

### 1. Tool Purpose and Description

Allows an LLM or AI agent to request the build of a specific Codomyrmex module. This can be used to ensure a module is up-to-date before deployment, testing, or other operations.

### 2. Invocation Name

`build_synthesis.start_module_build`

### 3. Input Schema (Parameters)

| Parameter Name    | Type      | Required | Description                                                              | Example Value                         |
| :---------------- | :-------- | :------- | :----------------------------------------------------------------------- | :------------------------------------ |
| `module_name`     | `string`  | Yes      | The name of the Codomyrmex module to build (e.g., `ai_code_editing`).      | `"data_visualization"`              |
| `build_target`    | `string`  | No       | Specific build target (e.g., `docker`, `wheel`). Default: `default`.       | `"docker_image"`                      |
| `clean_build`     | `boolean` | No       | Whether to perform a clean build. Default: `false`.                      | `true`                                |
| `async_execution` | `boolean` | No       | If true, tool returns immediately. Status via `build.get_build_status`. Default: `false`. | `true`                                |

**JSON Schema Example:**
```json
{
  "type": "object",
  "properties": {
    "module_name": {
      "type": "string",
      "description": "The name of the Codomyrmex module to build."
    },
    "build_target": {
      "type": "string",
      "description": "Specific build target. Default: default."
    },
    "clean_build": {
      "type": "boolean",
      "default": false
    },
    "async_execution": {
      "type": "boolean",
      "default": false
    }
  },
  "required": ["module_name"]
}
```

### 4. Output Schema (Return Value)

| Field Name | Type     | Description                                                                 | Example Value                               |
| :--------- | :------- | :-------------------------------------------------------------------------- | :------------------------------------------ |
| `build_id` | `string` | Unique ID for this build job.                                               | `"build_job_789"`                           |
| `status`   | `string` | `pending`, `running`, `succeeded`, `failed`. (If `async_execution` is false, will be a final state). | `"succeeded"`                               |
| `message`  | `string` | Summary message.                                                            | `"Build for data_visualization started."` |
| `artifacts_produced` | `array[string]` | List of primary artifact names produced.                   | `["data_vis.whl", "frontend_bundle.zip"]` |

**JSON Schema Example (for synchronous execution):**
```json
{
  "type": "object",
  "properties": {
    "build_id": { "type": "string" },
    "status": { "type": "string", "enum": ["pending", "running", "succeeded", "failed"] },
    "message": { "type": "string" },
    "artifacts_produced": {
        "type": "array",
        "items": { "type": "string"}
    }
  },
  "required": ["build_id", "status", "message"]
}
```

### 5. Error Handling

- `MODULE_NOT_FOUND`: The specified `module_name` does not exist.
- `BUILD_CONFIG_INVALID`: Build configuration for the module is missing or invalid.
- `BUILD_TOOL_ERROR`: An error occurred within the underlying build tool (e.g., Docker, Make).

### 6. Idempotency

- Not strictly idempotent if `clean_build` is false, as repeated builds might pick up changes. If `clean_build` is true, it's closer to idempotent for a given source version.
- Side Effects: Creates build artifacts, consumes system resources during build.

### 7. Usage Examples

**Example: Build the `data_visualization` module for Docker**
```json
{
  "tool_name": "build_synthesis.start_module_build",
  "arguments": {
    "module_name": "data_visualization",
    "build_target": "docker_image",
    "clean_build": true,
    "async_execution": true
  }
}
```

### 8. Security Considerations

- Build scripts (`Makefile`, `Dockerfile`, etc.) executed by this module can run arbitrary commands. Ensure build definitions are sourced from trusted locations and reviewed.
- Fetching dependencies during build can be a security risk (supply chain attacks). Use lockfiles and trusted registries.

--- 