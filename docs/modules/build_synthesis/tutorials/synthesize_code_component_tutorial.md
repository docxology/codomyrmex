# Build Synthesis - Tutorial: Synthesizing a New Codomyrmex Module with `synthesize_component_from_spec`

This tutorial guides you through using the `synthesize_component_from_spec` MCP tool from the Build Synthesis module to scaffold a new, standard Codomyrmex module structure using a specification and template.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Build Synthesis module installed and configured (see main [README.md](../../README.md)).
- The Codomyrmex project cloned and your current working directory is the root of the project.
- The `build_synthesis` module must have a pre-defined template for a "codomyrmex_module" (e.g., based on `template/module_template/` from the project root), and a way to interpret a module specification file.
- Familiarity with the standard Codomyrmex module structure and MCP tool invocation.

## 2. Goal

By the end of this tutorial, you will be able to:

- Successfully generate the basic directory structure and standard files for a new Codomyrmex module (e.g., `MyNewAnalyticsModule`) using `synthesize_component_from_spec`.
- Understand how to provide a `specification_file`, `language`, `target_directory`, and optional `template_name`.
- Verify the creation of the new module's files.

## 3. Steps

### Step 1: Plan Your New Module & Create Specification File

Decide on a name for your new module. For this tutorial, we will create a module named `MyNewAnalyticsModule`.
This module will be placed directly inside the main `codomyrmex/` project directory alongside other modules.

Create a specification file, say `specs/my_new_analytics_module_spec.json` in your project root:

```json
// specs/my_new_analytics_module_spec.json
{
  "module_name": "MyNewAnalyticsModule",
  "description": "A new module for performing advanced analytics.",
  "author": "Your Name",
  "email": "your.email@example.com",
  "language": "python" // Language can also be a top-level MCP parameter
}
```

### Step 2: Invoke `synthesize_component_from_spec`

We will use a hypothetical MCP client to call the tool. We'll reference the specification file and a template name (assuming `"codomyrmex_module_default_template"` is known to the system).

**Using a hypothetical MCP client:**

```bash
# Ensure you are in the Codomyrmex project root directory (e.g., /home/user/codomyrmex)
codomyrmex_mcp_client call build_synthesis synthesize_component_from_spec \
  --specification_file "specs/my_new_analytics_module_spec.json" \
  --language "python" \
  --target_directory "." \
  --template_name "codomyrmex_module_default_template"
```

**Parameters used:**
- `specification_file`: Path to the JSON (or YAML) file detailing the module.
- `language`: `"python"`. The target language for the module.
- `target_directory`: `"."`. The new module directory (`MyNewAnalyticsModule/`) will be created here (project root).
- `template_name`: `"codomyrmex_module_default_template"`. This tells the tool to use the standard template for a new Codomyrmex sub-module, augmented by the spec file.

### Step 3: Verify the Output/Generated Files

1.  **Check MCP Response**: The JSON response from the client should indicate success:
    ```json
    {
      "status": "success",
      "generated_files": {
        "MyNewAnalyticsModule/__init__.py": "...content...",
        "MyNewAnalyticsModule/README.md": "...content..."
        // ... other files mapped to their content or just listed as paths ...
      },
      "log_output": "Successfully synthesized component MyNewAnalyticsModule at ./MyNewAnalyticsModule based on spec and template.",
      "error_message": null
    }
    ```
    *(Note: The exact list of generated files depends on the template and how the tool reports them.)*

2.  **Verify Directory Structure and Files**: Check your project root for the new module directory:
    ```bash
    ls -l MyNewAnalyticsModule/
    tree MyNewAnalyticsModule/
    ```
    You should see the `MyNewAnalyticsModule` directory containing the standard set of files.

3.  **Inspect File Contents (Optional)**: Open some generated files (e.g., `MyNewAnalyticsModule/README.md`) to see if placeholders were correctly filled with information from your specification file.

## 4. Understanding the Results

The `synthesize_component_from_spec` tool used the specified template and your `specification_file` to generate a complete starter directory for `MyNewAnalyticsModule`. This scaffolding saves time and ensures consistency.

## 5. Troubleshooting

- **Error: `Template not found` or `Specification file error`**
  - **Cause**: The `template_name` is not recognized, the `specification_file` path is wrong, or the spec file is malformed.
  - **Solution**: 
    1. Verify template names and spec file paths/content.
    2. Check `MCP_TOOL_SPECIFICATION.md` for `synthesize_component_from_spec` details.
- **Error: `Output directory problem` or `Permission denied`**
  - **Cause**: The `target_directory` might be invalid, or no write permissions.
  - **Solution**: Ensure `target_directory` is valid and writable.
- **Files created but placeholders not filled correctly**: 
  - **Cause**: Template might not correctly use variables from the spec, or the spec file was malformed.
  - **Solution**: Check template files and spec file formatting/keys.

## 6. Next Steps

Congratulations on scaffolding a new Codomyrmex module using `synthesize_component_from_spec`!

Now you can:
- Develop functionality within `MyNewAnalyticsModule/`.
- Explore using different templates or more complex specifications.
- Consider using the `llm_assisted` flag if you need AI to help fill out template sections based on a more abstract spec. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)
