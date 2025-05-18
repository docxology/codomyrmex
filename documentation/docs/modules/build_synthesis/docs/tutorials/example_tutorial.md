---
id: build-synthesis-example-tutorial
title: Tutorial - Creating a Custom Build Target
sidebar_label: Custom Build Target Tutorial
---

# Build Synthesis Tutorial: Creating a Custom Build Target

This tutorial demonstrates how to define and use a custom build target within a module, managed by the Build Synthesis system.

## 1. Prerequisites

- Build Synthesis module is set up.
- A Codomyrmex module (e.g., `my_custom_module`) where you want to add a new build process.
- Basic understanding of Makefiles (or your chosen build tool for the example).

## 2. Goal

- Define a new build target named `docs_zip` for `my_custom_module` that creates a ZIP archive of its Markdown documentation files.
- Trigger this build target using the Build Synthesis module.

## 3. Steps

### Step 1: Define the Build Logic (e.g., in a Makefile)

In your `my_custom_module` directory, create or modify a `Makefile`:

```makefile
# my_custom_module/Makefile

# Assume markdown docs are in a 'manual_docs' subdirectory
DOC_FILES := $(wildcard manual_docs/*.md)

.PHONY: docs_zip
docs_zip:
    @echo "Zipping documentation..."
    @mkdir -p ../build_artifacts # Ensure artifact directory exists at project root + build_artifacts
    zip ../build_artifacts/my_custom_module_docs.zip $(DOC_FILES)
    @echo "Documentation zipped to ../build_artifacts/my_custom_module_docs.zip"

# Other build targets might exist (e.g., default, test)
default:
    @echo "Default build for my_custom_module"
```

Create some dummy markdown files in `my_custom_module/manual_docs/`:
```bash
mkdir -p my_custom_module/manual_docs
echo "# Page 1" > my_custom_module/manual_docs/page1.md
echo "# Page 2" > my_custom_module/manual_docs/page2.md
```

### Step 2: Configure Build Synthesis (Conceptual)

The Build Synthesis module needs to know about this `docs_zip` target. This might be through:
- A `build.yaml` (or similar) in `my_custom_module` that the Build Synthesis module parses.
- Conventions, if the Build Synthesis module is configured to recognize all PHONY targets in a Makefile.

**Conceptual `my_custom_module/build.yaml`:**
```yaml
version: 1
moduleName: my_custom_module
targets:
  - name: default
    command: "make default"
  - name: docs_zip
    command: "make docs_zip"
    description: "Creates a ZIP archive of Markdown documentation."
    artifacts:
      - path: "../build_artifacts/my_custom_module_docs.zip"
        type: "documentation_archive"
```

### Step 3: Trigger the Build via Build Synthesis

Use the MCP tool or API to trigger this new build target.

**Conceptual MCP Call (`build_synthesis.start_module_build`):**
```json
{
  "tool_name": "build_synthesis.start_module_build",
  "arguments": {
    "module_name": "my_custom_module",
    "build_target": "docs_zip"
  }
}
```

### Step 4: Verify the Output

- The Build Synthesis module should execute `make docs_zip` in the `my_custom_module` directory.
- A file `my_custom_module_docs.zip` should be created in the `codomyrmex/build_artifacts/` directory.
- The MCP tool call should return a success status and list the artifact.

**Example Output Snippet from MCP:**
```json
{
  "build_id": "build_docs_zip_abc",
  "status": "succeeded",
  "message": "Build for my_custom_module (docs_zip) completed.",
  "artifacts_produced": ["my_custom_module_docs.zip"]
}
```

## 4. Understanding the Results

You have successfully defined a custom build target within a module and triggered it through the Build Synthesis system. This allows for extensible and varied build processes beyond just compiling code, such as packaging documentation or other assets.

## 5. Troubleshooting

- **Makefile error / Command not found**:
  - **Solution**: Ensure `make` (or your chosen tool) is installed and PATH is correct. Test the Makefile target directly in the module's directory first (e.g., `cd my_custom_module && make docs_zip`).
- **Build Synthesis module doesn't recognize the target**:
  - **Solution**: Check the Build Synthesis module's configuration for `my_custom_module`. Ensure it correctly parses your `build.yaml` or that its conventions for discovering targets (e.g., from Makefiles) are being met.

## 6. Next Steps

- Explore defining build targets that depend on artifacts from other modules.
- Integrate artifact uploading to a central repository. 