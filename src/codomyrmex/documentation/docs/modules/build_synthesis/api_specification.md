# Build Synthesis - API Specification

## Introduction

The Build Synthesis module provides functionalities for automating build processes and synthesizing code components within the Codomyrmex project. While the primary programmatic interaction with this module is intended through its Model Context Protocol (MCP) tools, this document outlines the direct Python API functions available for more granular control or internal use by the MCP tool implementations or other modules.

For details on the MCP tools, please refer to the [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md).

## Core Python API Functions

This section details the Python API functions that underpin the Build Synthesis module's capabilities. These functions are typically called by the MCP tools or can be used internally.

### Build Orchestration

1.  **`trigger_build(target: str, config: dict = None, output_path_suggestion: str = None, clean_build: bool = False, build_options: dict = None) -> dict`**
    *   **Description**: Initiates a build process for a specified target (e.g., a component, module, or specific build configuration name).
    *   **Arguments**:
        *   `target` (str): Mandatory. Identifier for the build target (e.g., "module:ai_code_editing", "docker:my_service", "project_docs").
        *   `config` (dict, optional): A dictionary containing build configuration parameters, such as build profile (e.g., "debug", "release"), version information, or specific flags. Structure may vary based on target type.
        *   `output_path_suggestion` (str, optional): A suggested base directory where build artifacts should be placed. The actual path might be determined by the build system.
        *   `clean_build` (bool, optional): If `True`, forces a clean build, removing any prior artifacts. Default: `False`.
        *   `build_options` (dict, optional): Additional, potentially target-specific, build options or overrides.
    *   **Returns** (dict):
        ```json
        {
          "status": "success" | "failure" | "pending",
          "build_id": "unique_build_identifier_string", // Generated if build is asynchronous or long-running
          "message": "Build initiated successfully." | "Error message if immediate failure.",
          "artifact_paths": ["path/to/artifact1", "path/to/artifact2"], // Populated on synchronous success
          "log_output_summary": "Brief summary of build logs or initial log lines..." // Populated on synchronous success
        }
        ```

2.  **`get_build_status(build_id: str) -> dict`**
    *   **Description**: Retrieves the current status and details of a previously initiated build.
    *   **Arguments**:
        *   `build_id` (str): Mandatory. The unique identifier of the build, returned by `trigger_build`.
    *   **Returns** (dict):
        ```json
        {
          "build_id": "unique_build_identifier_string",
          "status": "pending" | "in_progress" | "success" | "failure" | "cancelled",
          "progress_percentage": 0-100, // Optional, if available
          "message": "Current status message (e.g., 'Compiling module X...', 'Build failed: Error Y').",
          "artifact_paths": ["path/to/artifact1"], // Populated on success
          "log_file_path": "path/to/full_build_log.txt", // Optional, path to detailed logs
          "error_details": "Detailed error if status is failure..."
        }
        ```

### Code Synthesis

1.  **`synthesize_component_from_prompt(prompt: str, language: str, target_directory: str, context_code: str = None, style_guide: str = None, llm_config: dict = None) -> dict`**
    *   **Description**: Generates a new code component (e.g., function, class, small module) based on a natural language prompt, using an LLM.
    *   **Arguments**:
        *   `prompt` (str): Mandatory. Detailed natural language description of the component to be synthesized.
        *   `language` (str): Mandatory. Target programming language (e.g., "python", "javascript").
        *   `target_directory` (str): Mandatory. The directory where the generated file(s) should be placed.
        *   `context_code` (str, optional): Existing code snippet(s) to provide context to the LLM.
        *   `style_guide` (str, optional): Instructions or examples related to coding style or conventions.
        *   `llm_config` (dict, optional): Configuration for the LLM (e.g., provider, model name, temperature). Defaults to module settings.
    *   **Returns** (dict):
        ```json
        {
          "status": "success" | "failure",
          "generated_files": {
            "filename1.ext": "content of file1...",
            "filename2.ext": "content of file2..."
          },
          "explanation": "LLM-generated explanation of the synthesized code (if any)...",
          "error_message": "Error details if any..."
        }
        ```

2.  **`synthesize_component_from_spec(specification_file: str, language: str, target_directory: str, template_name: str = None, llm_assisted: bool = False, llm_config: dict = None) -> dict`**
    *   **Description**: Generates a new code component based on a structured specification file (e.g., a JSON or YAML file defining component structure, interfaces, dependencies) or a pre-defined template.
    *   **Arguments**:
        *   `specification_file` (str): Mandatory. Path to the structured specification file for the component.
        *   `language` (str): Mandatory. Target programming language (if not implicitly defined by spec/template).
        *   `target_directory` (str): Mandatory. The directory where generated file(s) should be placed.
        *   `template_name` (str, optional): Name of a pre-defined component template to use as a base. The specification can augment or override template parts.
        *   `llm_assisted` (bool, optional): If `True`, an LLM may be used to fill in parts of the template or interpret parts of the specification. Default: `False`.
        *   `llm_config` (dict, optional): Configuration for the LLM if `llm_assisted` is `True`.
    *   **Returns** (dict):
        ```json
        {
          "status": "success" | "failure",
          "generated_files": {
            "filename1.ext": "content of file1...",
            "filename2.ext": "content of file2..."
          },
          "log_output": "Generation process summary...",
          "error_message": "Error details if any..."
        }
        ```

## Data Models

Data models for request and response payloads are defined by the Python function signatures and their return value dictionaries above. These also inform the structures used in the corresponding MCP tools (see `MCP_TOOL_SPECIFICATION.md`).

## Authentication & Authorization

Direct API access, if exposed externally from the Codomyrmex system, would require appropriate authentication and authorization mechanisms. Within the system, MCP tool usage is typically governed by the calling agent's permissions. These Python APIs assume they are called in an already authenticated and authorized context.

## Rate Limiting

As these API functions can trigger resource-intensive operations (builds, LLM calls), any external exposure should be protected by rate limiting. Internal usage should be mindful of resource consumption.

## Versioning

API versioning for these Python functions will follow standard Python library practices. Significant changes will be noted in the module's `CHANGELOG.md`. If the API is exposed more broadly, a formal versioning scheme might be adopted. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
