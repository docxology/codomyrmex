# Build Synthesis - Usage Examples

## Example 1: Basic Usage - Triggering a Build via MCP

<!-- TODO: Provide a simple, clear example of how to use a core feature. This example focuses on the `trigger_build` MCP tool. -->

```json
// Hypothetical MCP client request to trigger a build
{
  "tool_name": "trigger_build",
  "arguments": {
    "target_component": "my_python_module", // <!-- TODO: Replace with a realistic target component name -->
    "build_profile": "debug",
    "clean_build": true
  }
}
```

### Expected Outcome

<!-- TODO: Describe what the user should expect. 
This would be an MCP tool response. Show an example JSON response. -->
```json
// Example MCP tool response
{
  "status": "success", // or "failure"
  "artifact_paths": ["./output/builds/my_python_module/my_python_module.whl"], // <!-- TODO: Adjust path -->
  "log_output": "Build started for my_python_module... Build completed successfully.",
  "error_message": null
}
```

## Example 2: Advanced Scenario - Synthesizing a New Module via MCP

<!-- TODO: Illustrate a more complex use case, focusing on the `synthesize_code_component` MCP tool. -->

```json
// Hypothetical MCP client request to synthesize a new Codomyrmex module
{
  "tool_name": "synthesize_code_component",
  "arguments": {
    "component_type": "codomyrmex_module",
    "component_name": "NewDataProcessor",
    "output_directory": "./codomyrmex/", // <!-- TODO: Adjust base path if needed -->
    "specification": {
      "description": "A new module for processing specific data formats.",
      "initial_functions": ["process_data", "validate_schema"],
      "dependencies": ["pandas", "jsonschema"]
    }
  }
}
```

### Configuration (if any)

<!-- TODO: Detail any specific configuration needed for this example beyond the MCP call itself. 
E.g., existence of base `output_directory`, specific templates the tool might use. -->
- Ensure the `output_directory` (e.g., `./codomyrmex/`) is writable.
- The `synthesize_code_component` tool might rely on module templates located in `template/module_template/`.

### Expected Outcome

<!-- TODO: Describe the result. Show an example JSON response for the MCP tool. -->
```json
// Example MCP tool response
{
  "status": "success",
  "generated_files": [
    "./codomyrmex/new_data_processor/__init__.py",
    "./codomyrmex/new_data_processor/README.md",
    "./codomyrmex/new_data_processor/requirements.txt",
    "./codomyrmex/new_data_processor/src/new_data_processor.py"
    // ... other standard module files
  ],
  "log_output": "Successfully synthesized module NewDataProcessor.",
  "error_message": null
}
```
Files for the `NewDataProcessor` module would be created in the `codomyrmex/new_data_processor/` directory, based on the project's standard module template.

## Common Pitfalls & Troubleshooting

- **Issue**: Build failure (`trigger_build` returns `"status": "failure"`).
  - **Solution**: Check the `log_output` and `error_message` in the MCP response. Examine build logs if available at `artifact_paths`. Ensure all dependencies for the `target_component` are correctly installed and build scripts are valid.
- **Issue**: Code synthesis fails (`synthesize_code_component` returns `"status": "failure"`).
  - **Solution**: Verify the `component_type` is supported. Check `output_directory` permissions. Ensure the `specification` is valid for the chosen component type. Review logs for more details.
- **Issue**: Incorrect artifacts or synthesized code structure.
  - **Solution**: Review the build scripts for the target component. For synthesis, check the underlying templates and the input `specification` for correctness.

<!-- TODO: Add other common issues specific to build and synthesis tasks. --> 