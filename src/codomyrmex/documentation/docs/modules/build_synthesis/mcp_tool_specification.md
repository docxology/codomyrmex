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
- For asynchronous builds, `status` might be "pending", and subsequent status checks are needed via `get_build_status`.

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

## Tool: `get_build_status`

### 1. Tool Purpose and Description

Retrieves the current status and details of a previously initiated build using its `build_id`.
This tool maps to the `get_build_status` Python API function.

### 2. Invocation Name

`get_build_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type   | Required | Description                                          | Example Value           |
| :------------- | :----- | :------- | :--------------------------------------------------- | :---------------------- |
| `build_id`     | `string`| Yes      | The unique identifier of the build (from `trigger_build`). | `"build_job_170248A9Z"` |

### 4. Output Schema (Return Value)

| Field Name            | Type          | Description                                                                                             | Example Value                                                       |
| :-------------------- | :------------ | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------ |
| `build_id`            | `string`      | The build identifier.                                                                                   | `"build_job_170248A9Z"`                                             |
| `status`              | `string`      | Current build status: "pending", "in_progress", "success", "failure", "cancelled".                | `"in_progress"`                                                     |
| `progress_percentage` | `integer`     | Optional. Estimated completion percentage (0-100).                                                      | `75`                                                                |
| `message`             | `string`      | Current status message (e.g., "Compiling module X...", "Build failed: Error Y").                        | `"Linking final artifact..."`                                       |
| `artifact_paths`      | `array[string]`| List of paths to generated artifacts. Populated if `status` is "success".                               | `["./dist/core_library.whl"]`                                     |
| `log_file_path`       | `string`      | Optional. Path to a detailed build log file.                                                              | `"./output/logs/build_job_170248A9Z.log"`                         |
| `error_details`       | `string`      | Detailed error message if `status` is "failure".                                                          | `"Linker error: undefined symbol 'xyz'."`                           |

### 5. Error Handling

- If `build_id` is not found or invalid, an appropriate error status/message should be returned by the tool itself (e.g. status:"error", message: "Invalid build_id").

### 6. Idempotency

- **Idempotent**: Yes. Multiple calls with the same valid `build_id` should return the current state of that build without causing further side effects on the build itself.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "get_build_status",
  "arguments": {
    "build_id": "build_job_170248A9Z"
  }
}
```

### 8. Security Considerations

- Ensure `build_id` does not allow enumeration of arbitrary system information.
- Returned `log_file_path` or `artifact_paths` should be validated and within expected project boundaries.

---

## Tool: `synthesize_component_from_prompt`

### 1. Tool Purpose and Description

Generates a new code component (e.g., function, class, small module) based on a natural language prompt, primarily using an LLM.
This tool maps to the `synthesize_component_from_prompt` Python API function.

### 2. Invocation Name

`synthesize_component_from_prompt`

### 3. Input Schema (Parameters)

| Parameter Name    | Type     | Required | Description                                                                         | Example Value                                                                |
| :---------------- | :------- | :------- | :---------------------------------------------------------------------------------- | :--------------------------------------------------------------------------- |
| `prompt`          | `string` | Yes      | Detailed natural language description of the component to be synthesized.           | `"Create a Python function to calculate factorial recursively with a docstring."` |
| `language`        | `string` | Yes      | Target programming language (e.g., "python", "javascript").                         | `"python"`                                                                   |
| `target_directory`| `string` | Yes      | The directory where the generated file(s) should be placed.                         | `"./src/utils/"`                                                             |
| `context_code`    | `string` | No       | Existing code snippet(s) to provide context to the LLM.                             | `"class MathHelpers:
    # new function will be part of this class"`          |
| `style_guide`     | `string` | No       | Instructions or examples related to coding style or conventions.                    | `"Follow PEP8. Max line length 88."`                                       |
| `llm_config`      | `object` | No       | Configuration for the LLM (e.g., provider, model name). Defaults to module settings.| `{"model_name": "gpt-4-turbo"}`                                              |

### 4. Output Schema (Return Value)

| Field Name        | Type     | Description                                                                                               | Example Value                                                                   |
| :---------------- | :------- | :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| `status`          | `string` | Synthesis status: "success", "failure".                                                                   | `"success"`                                                                     |
| `generated_files` | `object` | A dictionary where keys are filenames and values are the string content of the generated files.             | `{"factorial.py": "def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)"}` |
| `explanation`     | `string` | LLM-generated explanation of the synthesized code (if any).                                               | `"This function calculates factorial using recursion..."`                     |
| `error_message`   | `string` | Error description if `status` is "failure".                                                               | `"LLM request failed due to invalid API key."`                                |

### 5. Error Handling

- Errors such as LLM failures, invalid prompts, or file system write issues will result in a "failure" `status`.

### 6. Idempotency

- **Idempotent**: No. Re-running with the same parameters will likely attempt to create and write the same files, potentially overwriting or erroring if they exist.
- **Explanation**: Strong side effects on the file system.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "synthesize_component_from_prompt",
  "arguments": {
    "prompt": "Generate a Python class for a simple User with name and email attributes.",
    "language": "python",
    "target_directory": "./models/",
    "style_guide": "Include type hints."
  }
}
```

### 8. Security Considerations

- **File System Writes**: Validate `target_directory` to prevent writing outside intended project areas.
- **Prompt Injection**: If `prompt`, `context_code`, or `style_guide` can be influenced by untrusted external sources, this could lead to prompt injection attacks against the LLM.
- **Resource Usage**: LLM calls can be resource-intensive (API costs, time).

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
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
