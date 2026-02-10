# Build Synthesis - MCP Tool Specification

This document outlines the specification for tools within the Build Synthesis module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Dependencies**: Tools may rely on build systems (e.g., Make, Docker, language-specific build tools) and templating engines.
- **File System Access**: These tools will likely interact extensively with the file system to read sources, write artifacts, and generate code.
- **Alignment with Python API**: The MCP tools defined here are designed to be wrappers or interfaces to the core Python API functions detailed in `API_SPECIFICATION.md`. Parameter names and functionalities should closely align.

---

## Tool: `trigger_build`

### 1. Tool Purpose and Description

Initiates a build process for a specified target (e.g., a component, module, or specific build configuration name).
This tool maps to the `trigger_build` Python API function.

### 2. Invocation Name

`trigger_build`

### 3. Input Schema (Parameters)

| Parameter Name          | Type    | Required | Description                                                                                                   | Example Value                                            |
| :---------------------- | :------ | :------- | :------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------- |
| `target`                | `string`| Yes      | Identifier for the build target (e.g., "module:ai_code_editing", "docker:my_service", "project_docs").       | `"module:ai_code_editing"`                                 |
| `config`                | `object`| No       | Build configuration parameters (e.g., profile, version). Structure may vary based on target.                | `{"profile": "release", "version": "1.2.0"}`              |
| `output_path_suggestion`| `string`| No       | Suggested base directory for build artifacts.                                                                 | `"./output/builds/"`                                     |
| `clean_build`           | `boolean`| No       | If `True`, forces a clean build. Default: `False`.                                                              | `true`                                                   |
| `build_options`         | `object`| No       | Additional, potentially target-specific, build options or overrides.                                        | `{"skip_tests": true, "verbose_logging": false}`      |

### 4. Output Schema (Return Value)

| Field Name             | Type          | Description                                                                                                  | Example Value                                                        |
| :--------------------- | :------------ | :----------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| `status`               | `string`      | Build initiation status: "success", "failure", "pending".                                                    | `"pending"`                                                          |
| `build_id`             | `string`      | Unique identifier for the build, especially if asynchronous. Empty if build failed immediately.              | `"build_job_170248A9Z"`                                              |
| `message`              | `string`      | Message about the initiation status or immediate error.                                                      | `"Build for target 'module:ai_code_editing' initiated."`              |
| `artifact_paths`       | `array[string]`| List of paths to generated artifacts if build completes synchronously and successfully. May be empty.          | `["./dist/ai_code_editing.whl"]`                                   |
| `log_output_summary`   | `string`      | Brief summary of build logs or initial log lines if build completes synchronously.                           | `"Initial compilation started..."`                                   |
| `error_message`        | `string`      | Error description if immediate `status` is "failure".                                                          | `"Invalid target specified."`                                        |

### 5. Error Handling

- Immediate failures (e.g., invalid `target`) result in a "failure" `status` and `error_message`.
- For asynchronous builds, `status` might be "pending", and the caller should poll or wait before checking results.

### 6. Idempotency

- **Idempotent**: Generally No. Re-running a build typically overwrites previous artifacts or creates new ones.
- **Explanation**: Side effects include file system changes. A `clean_build` option further modifies behavior.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "trigger_build",
  "arguments": {
    "target": "module:core_library",
    "config": {"profile": "release"},
    "clean_build": true
  }
}
```

### 8. Security Considerations

- **Command Injection**: Build scripts or commands invoked must be carefully constructed if `target` or `build_options` influence command execution.
- **Resource Usage**: Builds can be resource-intensive.
- **Dependency Security**: Build process might download dependencies; their security should be considered.

---

## Tool: `clean_build`

### 1. Tool Purpose and Description

Cleans build artifacts for a specific target or all targets. Removes generated files from the build directory.
This tool maps to the `BuildManager.clean_build` Python API method.

### 2. Invocation Name

`clean_build`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                                              | Example Value       |
| :------------- | :------- | :------- | :----------------------------------------------------------------------- | :------------------ |
| `target_name`  | `string` | No       | Name of the build target to clean. If omitted, cleans all build artifacts. | `"core_library"`  |
| `config_path`  | `string` | No       | Path to build configuration file. Defaults to `build.yaml` in project root. | `"./build.yaml"` |

### 4. Output Schema (Return Value)

| Field Name | Type      | Description                                           | Example Value |
| :--------- | :-------- | :---------------------------------------------------- | :------------ |
| `success`  | `boolean` | Whether the clean operation completed successfully.   | `true`        |
| `message`  | `string`  | Description of what was cleaned or error details.     | `"Cleaned build directory for target: core_library"` |

### 5. Error Handling

- File system permission errors or missing directories result in `success: false` with an error message.

### 6. Idempotency

- **Idempotent**: Yes. Cleaning an already-clean directory is a no-op that succeeds.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "clean_build",
  "arguments": {
    "target_name": "core_library"
  }
}
```

### 8. Security Considerations

- **Path Traversal**: Validate `target_name` to prevent deletion of files outside the build directory.
- **Permissions**: Tool needs appropriate write/delete permissions on the build directory.

---

## Tool: `package_artifacts`

### 1. Tool Purpose and Description

Packages build artifacts for a specific target into a compressed archive (`.tar.gz`).
This tool maps to the `BuildManager.package_artifacts` Python API method.

### 2. Invocation Name

`package_artifacts`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                                              | Example Value                        |
| :------------- | :------- | :------- | :----------------------------------------------------------------------- | :----------------------------------- |
| `target_name`  | `string` | Yes      | Name of the build target whose artifacts should be packaged.             | `"core_library"`                     |
| `output_path`  | `string` | No       | Path for the output archive. Defaults to `{target}_{timestamp}.tar.gz`. | `"./dist/core_library_release.tar.gz"` |

### 4. Output Schema (Return Value)

| Field Name     | Type     | Description                                              | Example Value                              |
| :------------- | :------- | :------------------------------------------------------- | :----------------------------------------- |
| `status`       | `string` | Packaging status: "success", "failure".                  | `"success"`                                |
| `archive_path` | `string` | Path to the generated archive file.                      | `"./dist/core_library_20260210_120000.tar.gz"` |
| `error_message`| `string` | Error description if `status` is "failure".              | `"Build directory not found: build/core_library"` |

### 5. Error Handling

- Missing build directories or file system errors result in a "failure" `status`.

### 6. Idempotency

- **Idempotent**: No. Re-running overwrites the output archive if it exists or creates a new timestamped one.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "package_artifacts",
  "arguments": {
    "target_name": "core_library",
    "output_path": "./dist/core_library_release.tar.gz"
  }
}
```

### 8. Security Considerations

- **Path Traversal**: Validate `output_path` to prevent writing outside intended directories.
- **Archive Size**: Large build directories could produce very large archives; consider size limits.

---

## Tool: `get_build_summary`

### 1. Tool Purpose and Description

Returns a summary of all builds that have been executed, including counts, success rates, and average duration.
This tool maps to the `BuildManager.get_build_summary` Python API method.

### 2. Invocation Name

`get_build_summary`

### 3. Input Schema (Parameters)

| Parameter Name | Type     | Required | Description                                                              | Example Value    |
| :------------- | :------- | :------- | :----------------------------------------------------------------------- | :--------------- |
| `config_path`  | `string` | No       | Path to build configuration file. Defaults to `build.yaml` in project root. | `"./build.yaml"` |

### 4. Output Schema (Return Value)

| Field Name        | Type      | Description                                         | Example Value |
| :---------------- | :-------- | :-------------------------------------------------- | :------------ |
| `total_builds`    | `integer` | Total number of builds executed.                    | `10`          |
| `successful`      | `integer` | Number of successful builds.                        | `8`           |
| `failed`          | `integer` | Number of failed builds.                            | `2`           |
| `success_rate`    | `number`  | Ratio of successful builds to total (0.0 to 1.0).  | `0.8`         |
| `average_duration`| `number`  | Average build duration in seconds.                  | `45.3`        |

### 5. Error Handling

- Returns zero counts if no builds have been executed yet.

### 6. Idempotency

- **Idempotent**: Yes. Read-only operation that does not modify state.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "get_build_summary",
  "arguments": {}
}
```

### 8. Security Considerations

- No significant security concerns as this is a read-only operation returning aggregate data.

---

## Tool: `synthesize_component_from_spec`

### 1. Tool Purpose and Description

Generates a new code component based on a structured specification file (e.g., a JSON or YAML file) or a pre-defined template.
This tool maps to the `synthesize_component_from_spec` Python API function.

### 2. Invocation Name

`synthesize_component_from_spec`

### 3. Input Schema (Parameters)

| Parameter Name       | Type    | Required | Description                                                                                                | Example Value                               |
| :------------------- | :------ | :------- | :--------------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| `specification_file` | `string`| Yes      | Path to the structured specification file (e.g., JSON, YAML) for the component.                            | `"./specs/new_module_spec.json"`            |
| `language`           | `string`| Yes      | Target programming language (if not implicitly defined by spec/template).                                  | `"python"`                                  |
| `target_directory`   | `string`| Yes      | The directory where generated file(s) should be placed.                                                    | `"./codomyrmex_modules/"`                   |
| `template_name`      | `string`| No       | Name of a pre-defined component template to use. The specification can augment/override template parts.      | `"default_codomyrmex_module_v1"`            |
| `llm_assisted`       | `boolean`| No       | If `True`, an LLM may be used to fill in parts of the template or interpret parts of the spec. Default: `False`. | `true`                                      |
| `llm_config`         | `object`| No       | Configuration for the LLM if `llm_assisted` is `True`. Defaults to module settings.                        | `{"model_name": "gpt-3.5-turbo"}`           |

### 4. Output Schema (Return Value)

| Field Name        | Type     | Description                                                                                               | Example Value                                                              |
| :---------------- | :------- | :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `status`          | `string` | Synthesis status: "success", "failure".                                                                   | `"success"`                                                                |
| `generated_files` | `object` | A dictionary where keys are filenames and values are the string content of the generated files.             | `{"my_new_module/__init__.py": "", "my_new_module/main.py": "# Main logic"}` |
| `log_output`      | `string` | Summary of the synthesis process or key messages.                                                           | `"Generated 2 files for component based on spec_v1.json."`               |
| `error_message`   | `string` | Error description if `status` is "failure".                                                               | `"Template 'invalid_template' not found."`                               |

### 5. Error Handling

- Errors such as missing/invalid `specification_file`, template issues, or file system write failures will result in a "failure" `status`.

### 6. Idempotency

- **Idempotent**: No. Re-running would likely attempt to create the same files, potentially failing or overwriting if they exist.
- **Explanation**: Strong side effects on the file system.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "synthesize_component_from_spec",
  "arguments": {
    "specification_file": "./module_specs/user_service.yaml",
    "language": "python",
    "target_directory": "./services/user_service/",
    "template_name": "fastapi_service_template"
  }
}
```

### 8. Security Considerations

- **File System Writes**: Validate `target_directory` to prevent writing outside intended project areas.
- **Code Injection in Templates/Specs**: If templates or specification files can embed user-controlled strings directly into generated code without sanitization, this could be a risk.
- **Specification File Parsing**: Ensure robust and secure parsing of `specification_file` to prevent vulnerabilities from malformed spec files (e.g., XML DTD attacks if XML is used, etc.).
- **Permissions**: Tool needs appropriate write permissions.

--- 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
