# Build Synthesis - Usage Examples

# Build Synthesis - Usage Examples

## Example 1: Basic Usage - Triggering a Build via MCP

This example demonstrates how to trigger a build for a specific component using the `trigger_build` MCP tool. This is the primary way to generate distribution artifacts (wheels, etc.) for Codomyrmex modules.

```json
{
  "tool_name": "trigger_build",
  "arguments": {
    "target_component": "ai_code_editing",
    "build_profile": "release",
    "clean_build": true
  }
}
```

### Expected Outcome

The tool will return an MCP JSON response indicating the status and the location of the generated artifacts.

```json
{
  "status": "success",
  "artifact_paths": ["./src/codomyrmex/agents/ai_code_editing/dist/codomyrmex_ai_code_editing-0.1.0-py3-none-any.whl"],
  "log_output": "Build started for ai_code_editing... Running build scripts... Build completed successfully.",
  "error_message": null
}
```

## Example 2: Advanced Scenario - Synthesizing a New Module via MCP

The `synthesize_code_component` tool allows for the rapid creation of new, standardized Codomyrmex modules based on a high-level specification.

```json
{
  "tool_name": "synthesize_code_component",
  "arguments": {
    "component_type": "codomyrmex_module",
    "component_name": "SecurityScanner",
    "output_directory": "./src/codomyrmex/",
    "specification": {
      "description": "A module for identifying potential security vulnerabilities in Python code.",
      "initial_functions": ["scan_file", "report_vulnerabilities"],
      "dependencies": ["bandit", "safety"]
    }
  }
}
```

### Configuration

- Ensure the `output_directory` is within the `src/codomyrmex/` namespace to follow project standards.
- The tool uses the centralized module template located in `src/codomyrmex/module_template/`.

### Expected Outcome

Successful synthesis will create a full directory structure with localized documentation and initial code skeletons.

```json
{
  "status": "success",
  "generated_files": [
    "./src/codomyrmex/security_scanner/__init__.py",
    "./src/codomyrmex/security_scanner/README.md",
    "./src/codomyrmex/security_scanner/SPEC.md",
    "./src/codomyrmex/security_scanner/AGENTS.md",
    "./src/codomyrmex/security_scanner/requirements.txt",
    "./src/codomyrmex/security_scanner/src/security_scanner.py"
  ],
  "log_output": "Successfully synthesized module SecurityScanner from template.",
  "error_message": null
}
```

## Common Pitfalls & Troubleshooting

- **Issue**: **Build Failure** (`trigger_build` returns `"status": "failure"`)
  - **Solution**: Check the `error_message` in the MCP response. Ensure the `target_component` directory exists and contains a valid `setup.py` or `pyproject.toml`.

- **Issue**: **Synthesis Failure** (`synthesize_code_component` returns `"status": "failure"`)
  - **Solution**: Verify `component_type` is one of the supported types (e.g., `codomyrmex_module`). Ensure the `output_directory` is writable.

- **Issue**: **Missing Dependencies** in synthesized modules.
  - **Solution**: Add any missing third-party packages to the `specification` arguments under `dependencies` and re-run synthesis, or manually update the generated `requirements.txt`.

- **Issue**: **Signposting Drift**
  - **Solution**: After synthesis, it is recommended to run `scripts/documentation/doc_scaffolder.py` to ensure all parent/child links are correctly populated in the new directory.
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
