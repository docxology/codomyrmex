# Build Synthesis - Example Tutorial: Getting Started with [Feature X]

<!-- TODO: Replace '[Feature X]' in the title and throughout this tutorial with a specific, key feature of the Build Synthesis module. 
    Examples: 
    - "Triggering a Python Module Build using `trigger_build`"
    - "Synthesizing a New Codomyrmex Module using `synthesize_code_component`"
    - "Building a Docker Image for a Service" 
-->

This tutorial will guide you through the process of using [Feature X] of the Build Synthesis module.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Build Synthesis module installed and configured (see main [README.md](../../README.md)).
- <!-- TODO: List any specific tools, accounts, or data needed for *this specific tutorial*. 
    E.g., For `trigger_build`: "A Codomyrmex module (e.g., `data_visualization`) with a valid `pyproject.toml` or Makefile."
    E.g., For `synthesize_code_component`: "Access to the Codomyrmex project structure where the new module will be placed." -->
- Familiarity with <!-- TODO: Basic concepts related to the module or feature. E.g., "Python packaging concepts (wheel, sdist)", "Codomyrmex module structure", "MCP tool invocation if using a client". -->

## 2. Goal

By the end of this tutorial, you will be able to:

- <!-- TODO: State the primary learning objective. E.g., "Successfully trigger a build for the `data_visualization` module and locate its packaged wheel file." -->
- <!-- TODO: Understand the basic workflow of [Feature X]. E.g., "Understand how to specify a `target_component` for the `trigger_build` tool and interpret its output containing artifact paths." -->

## 3. Steps

### Step 1: Prepare Your Input/Environment

<!-- TODO: Describe how to prepare any necessary input data or environment for the tutorial. 
    This might involve ensuring a specific module exists, or that build tools are in the PATH. -->

```bash
# Example: If [Feature X] is `trigger_build` for a Python module `my_module`
# Ensure `my_module` exists and has a `pyproject.toml` or `setup.py` for building.
# Ensure build tools like `python -m build` are available.
cd /path/to/your/codomyrmex/project/root 
# Make sure the module to be built (e.g., my_module) is present here.
```

### Step 2: Invoke [Feature X]

<!-- TODO: Provide clear, step-by-step instructions on how to use the feature. 
    Show how to call the relevant MCP tool (trigger_build or synthesize_code_component) or a direct command if applicable. -->

**Using a hypothetical MCP client (example for `trigger_build`):**

```bash
# <!-- TODO: Replace with actual command or illustrate client library usage -->
# codomyrmex_mcp_client call build_synthesis trigger_build \
#   --target_component "data_visualization" \
#   --build_profile "release" \
#   --clean_build true \
#   --output_path "./output/custom_builds/"
```

**Using a hypothetical MCP client (example for `synthesize_code_component`):**

```bash
# <!-- TODO: Replace with actual command or illustrate client library usage -->
# codomyrmex_mcp_client call build_synthesis synthesize_code_component \
#   --component_type "codomyrmex_module" \
#   --component_name "MyNewServiceModule" \
#   --output_directory "./codomyrmex/" \
#   --specification '{"description": "A service module for X", "language": "python"}'
```

### Step 3: Verify the Output/Artifacts

<!-- TODO: Explain how to check if the feature worked correctly. 
    For `trigger_build`, this means checking the MCP response for artifact paths and verifying those files exist. 
    For `synthesize_code_component`, check the response for generated file paths and verify the directory structure. -->

- Check the JSON response from the MCP client for `"status": "success"`.
- For `trigger_build`, inspect the `"artifact_paths"` array and verify the existence of files (e.g., a `.whl` file in `output/custom_builds/data_visualization/` or similar).
- For `synthesize_code_component`, inspect `"generated_files"` and verify the new module directory (e.g., `codomyrmex/MyNewServiceModule/`) and its standard files have been created.

## 4. Understanding the Results

<!-- TODO: Briefly explain the output or outcome. 
    What do the generated artifacts represent? What is the structure of the synthesized module? -->

## 5. Troubleshooting

- **Error: `Build failed for target_component` (from `trigger_build`)**
  - **Cause**: Issues with the component's build scripts, missing dependencies for that component, or toolchain errors (compiler, linker).
  - **Solution**: 
    1. Examine the `log_output` and `error_message` in the MCP response.
    2. Manually try to build the `target_component` in its own directory to isolate the issue.
    3. Ensure all its dependencies (from its own `requirements.txt` or similar) are installed.
- **Error: `Component type not supported` or `Template not found` (from `synthesize_code_component`)**
  - **Cause**: The requested `component_type` might not be defined, or the specified `template_name` (if used) doesn't exist.
  - **Solution**: 
    1. Check the `MCP_TOOL_SPECIFICATION.md` for supported `component_type` values.
    2. Ensure any referenced templates are correctly placed and named within the `template/` directory structure.

<!-- TODO: Add other common issues specific to build or synthesis features. -->

## 6. Next Steps

Congratulations on completing this tutorial on [Feature X]!

Now you can try:
- <!-- TODO: Suggest next steps relevant to [Feature X] and the Build Synthesis module. -->
- Building other modules within the Codomyrmex project.
- Exploring different `build_profile` options.
- Customizing the `specification` for `synthesize_code_component` to create more tailored modules.
- Integrating these build/synthesis steps into a CI/CD pipeline. 