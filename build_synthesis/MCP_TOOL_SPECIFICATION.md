# Build Synthesis - MCP Tool Specification

This document outlines the specification for tools within the Build Synthesis module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Dependencies**: Tools may rely on build systems (e.g., Make, Docker, language-specific build tools) and templating engines.
- **File System Access**: These tools will likely interact extensively with the file system to read sources, write artifacts, and generate code.

---

## Tool: `trigger_build`

### 1. Tool Purpose and Description

Triggers a build process for a specified component or target within the project. This could involve compiling code, packaging artifacts, or running build scripts.

### 2. Invocation Name

`trigger_build`

### 3. Input Schema (Parameters)

| Parameter Name    | Type     | Required | Description                                                                                                | Example Value                               |
| :---------------- | :------- | :------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| `target_component`| `string` | Yes      | Identifier for the component or build target (e.g., module name, specific script, Docker image tag part).    | `"data_visualization_module"` or `"main_app"` |
| `build_profile`   | `string` | No       | Optional build profile or configuration (e.g., "debug", "release", "test"). Default: `"default"`.        | `"release"`                                 |
| `output_path`     | `string` | No       | Suggested path for build artifacts. Module may override or use predefined paths.                           | `"./output/builds/"`                        |
| `clean_build`     | `boolean`| No       | Whether to perform a clean build (e.g., remove previous artifacts before building). Default: `false`.      | `true`                                      |
| `options`         | `object` | No       | Additional build-specific options.                                                                         | `{"skip_tests": true}`                     |

### 4. Output Schema (Return Value)

| Field Name      | Type     | Description                                                                                      | Example Value                                              |
| :-------------- | :------- | :----------------------------------------------------------------------------------------------- | :--------------------------------------------------------- |
| `status`        | `string` | Build status: "success", "failure", "partial_success".                                           | `"success"`                                                |
| `artifact_paths`| `array[string]` | List of paths to generated artifacts (e.g., executables, libraries, archives, image IDs). Empty if none. | `["./dist/my_app.whl", "./output/reports/build.log"]` |
| `log_output`    | `string` | A summary or key excerpts from the build log. Full log may be in `artifact_paths`.               | `"Build completed in 120s. 2 warnings."`                 |
| `error_message` | `string` | Error description if `status` is "failure".                                                      | `"Compilation failed for module X."`                     |

### 5. Error Handling

- Build failures will result in a "failure" status and details in `error_message` and `log_output`.
- Configuration errors (e.g., invalid `target_component`) will also be reported.

### 6. Idempotency

- **Idempotent**: Generally No. Re-running a build typically overwrites previous artifacts or creates new ones, potentially with different timestamps or content if sources changed.
- **Explanation**: Side effects include file system changes. A `clean_build` option further modifies behavior.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "trigger_build",
  "arguments": {
    "target_component": "core_library",
    "build_profile": "release",
    "clean_build": true
  }
}
```

### 8. Security Considerations

- **Command Injection**: Build scripts or commands invoked must be carefully constructed to avoid injection vulnerabilities if `target_component` or `options` influence command execution.
- **Resource Usage**: Builds can be resource-intensive. Consider safeguards against excessive CPU/memory/disk usage.
- **Dependency Security**: The build process might download or use third-party dependencies; their security should be considered (though this is a broader project concern).

---

## Tool: `synthesize_code_component`

### 1. Tool Purpose and Description

Generates code for a new software component (e.g., a new module, class, function boilerplate) based on a provided specification or template.

### 2. Invocation Name

`synthesize_code_component`

### 3. Input Schema (Parameters)

| Parameter Name      | Type     | Required | Description                                                                                                | Example Value                                                               |
| :------------------ | :------- | :------- | :--------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| `component_type`    | `string` | Yes      | Type of component to synthesize (e.g., "codomyrmex_module", "python_class", "api_endpoint").                | `"codomyrmex_module"`                                                         |
| `component_name`    | `string` | Yes      | Name for the new component (e.g., "MyNewModule", "UserService").                                           | `"MyNewUtility"`                                                            |
| `output_directory`  | `string` | Yes      | Base directory where the new component's files should be generated (e.g., `"./modules/"`, `"./src/services/"`). | `"./codomyrmex/"`                                                              |
| `specification`     | `object` | No       | Detailed specification for the component, structure depends on `component_type`. (e.g., for a class: methods, attributes). | `{"module_description": "Handles user authentication."}`                     |
| `template_name`     | `string` | No       | Name of a pre-defined template to use for synthesis. May override or supplement `specification`.         | `"default_rest_controller"`                                                 |

### 4. Output Schema (Return Value)

| Field Name        | Type          | Description                                                                            | Example Value                                                              |
| :---------------- | :------------ | :------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `status`          | `string`      | Synthesis status: "success", "failure", "partial_success".                             | `"success"`                                                                |
| `generated_files` | `array[string]`| List of paths to the files and directories created for the new component.              | `["./codomyrmex/my_new_utility/__init__.py", "./codomyrmex/my_new_utility/README.md"]` |
| `log_output`      | `string`      | Summary of the synthesis process or key messages.                                        | `"Generated module MyNewUtility with 3 files."`                            |
| `error_message`   | `string`      | Error description if `status` is "failure".                                            | `"Component type 'unknown_type' not supported."`                           |

### 5. Error Handling

- Errors such as invalid `component_type`, issues with `specification`, or file system write failures will result in a "failure" status.

### 6. Idempotency

- **Idempotent**: Generally No. Re-running with the same parameters would likely attempt to create the same files, potentially failing or overwriting if they already exist.
- **Explanation**: Strong side effects on the file system. Some implementations might offer an `overwrite` flag.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "synthesize_code_component",
  "arguments": {
    "component_type": "codomyrmex_module",
    "component_name": "NewReportingModule",
    "output_directory": "./codomyrmex/",
    "specification": {
      "description": "A module for generating weekly reports.",
      "initial_functions": ["generate_report", "email_report"]
    }
  }
}
```

### 8. Security Considerations

- **File System Writes**: Must ensure that `output_directory` and `component_name` are validated to prevent writing outside of intended project areas (path traversal vulnerabilities).
- **Code Injection in Templates**: If synthesis uses templates that can embed parts of `specification` or `component_name` directly into code, these inputs must be sanitized to prevent code injection into the generated files.
- **Permissions**: The tool needs appropriate write permissions for the `output_directory`.

--- 