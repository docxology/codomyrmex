# Documentation - MCP Tool Specification

This document outlines the specification for tools within the Documentation module that are intended to be integrated with the Model Context Protocol (MCP). These tools primarily interact with the Docusaurus documentation website generation process.

## General Considerations

- **Dependencies**: These tools rely on Node.js, npm/yarn, and the Docusaurus installation within the `documentation` module directory.
- **Working Directory**: Operations are typically performed relative to the `documentation` module directory or the project root.
- **File System Access**: Tools will interact with the file system to run builds and potentially serve content.

---

## Tool: `trigger_documentation_build`

### 1. Tool Purpose and Description

Triggers the build process for the Docusaurus documentation website. This generates a static version of the site.

### 2. Invocation Name

`trigger_documentation_build`

### 3. Input Schema (Parameters)

| Parameter Name    | Type     | Required | Description                                                                                           | Example Value |
| :---------------- | :------- | :------- | :---------------------------------------------------------------------------------------------------- | :------------ |
| `clean_build`     | `boolean`| No       | Whether to perform a clean build (e.g., remove previous `build` directory contents). Default: `false`. | `true`        |
| `package_manager` | `string` | No       | Specifies the package manager to use (`"npm"` or `"yarn"`). Default: `"npm"`.                      | `"yarn"`      |

### 4. Output Schema (Return Value)

| Field Name      | Type     | Description                                                                            | Example Value                                      |
| :-------------- | :------- | :------------------------------------------------------------------------------------- | :------------------------------------------------- |
| `status`        | `string` | Build status: "success", "failure".                                                    | `"success"`                                        |
| `output_path`   | `string` | Path to the directory containing the built static site (e.g., `"documentation/build/"`). | `"./documentation/build/"`                       |
| `log_output`    | `string` | A summary or key excerpts from the build log.                                          | `"Docusaurus build completed successfully."`       |
| `error_message` | `string` | Error description if `status` is "failure".                                            | `"npm run build command failed with exit code 1."` |

### 5. Error Handling

- Failures during the build process (e.g., Docusaurus errors, command execution failures) will result in a "failure" status and details in `error_message` and `log_output`.

### 6. Idempotency

- **Idempotent**: No, if `clean_build` is false and sources change. Yes, if `clean_build` is true and sources are the same (though timestamps might differ).
- **Explanation**: The build process modifies the `documentation/build` directory. Subsequent calls can produce different results if underlying documentation source files have changed.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "trigger_documentation_build",
  "arguments": {
    "clean_build": true,
    "package_manager": "yarn"
  }
}
```

### 8. Security Considerations

- **Command Execution**: Ensures that only predefined build commands are executed. No arbitrary command execution based on input.
- **Resource Usage**: Documentation builds can consume resources. Ensure this is managed if run in constrained environments.

---

## Tool: `check_documentation_environment`

### 1. Tool Purpose and Description

Checks if the necessary environment (Node.js, npm/yarn) for building and serving the Docusaurus documentation is correctly set up.

### 2. Invocation Name

`check_documentation_environment`

### 3. Input Schema (Parameters)

(This tool currently takes no input parameters.)

### 4. Output Schema (Return Value)

| Field Name      | Type     | Description                                                                      | Example Value                                                |
| :-------------- | :------- | :------------------------------------------------------------------------------- | :----------------------------------------------------------- |
| `status`        | `string` | Overall check status: "success" (all good), "warning" (minor issues), "error" (major issues). | `"success"`                                                  |
| `node_detected` | `boolean`| Whether Node.js was found.                                                         | `true`                                                       |
| `node_version`  | `string` | Detected Node.js version, or null if not found.                                  | `"v18.16.0"`                                                 |
| `npm_detected`  | `boolean`| Whether npm was found.                                                             | `true`                                                       |
| `npm_version`   | `string` | Detected npm version, or null if not found.                                      | `"9.5.1"`                                                    |
| `yarn_detected` | `boolean`| Whether yarn was found.                                                            | `false`                                                      |
| `yarn_version`  | `string` | Detected yarn version, or null if not found.                                     | `null`                                                       |
| `message`       | `string` | A summary message about the environment status.                                    | `"Node.js and npm detected. Yarn not found (optional)."`       |

### 5. Error Handling

- Errors during command execution (e.g., `node --version`) are caught and reflected in the status and message.

### 6. Idempotency

- **Idempotent**: Yes. Checking the environment does not change its state.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "check_documentation_environment",
  "arguments": {}
}
```

### 8. Security Considerations

- Executes version checking commands (`node --version`, etc.). Assumes these commands are safe and do not pose a risk in the execution environment.

--- 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
