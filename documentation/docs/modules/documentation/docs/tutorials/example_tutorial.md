---
sidebar_label: 'Adding New Module Docs'
title: 'Tutorial: Adding a New Module to Documentation'
---

# Tutorial: Adding a New Module to the Codomyrmex Documentation

This tutorial guides you through the process of integrating documentation from a new or existing Codomyrmex module into the central Docusaurus-based documentation website.

## 1. Prerequisites

Before you begin, ensure you have the following:

- A local clone of the Codomyrmex repository.
- Node.js and npm/yarn installed (see [Development Setup](../../../../development/environment-setup.md)).
- The module you want to add documentation for (let's call it `new_module`) should ideally follow the standard Codomyrmex documentation file structure:
    - `new_module/README.md` (Module overview)
    - `new_module/API_SPECIFICATION.md`
    - `new_module/MCP_TOOL_SPECIFICATION.md`
    - `new_module/CHANGELOG.md`
    - `new_module/SECURITY.md`
    - `new_module/USAGE_EXAMPLES.md`
    - `new_module/docs/index.md` (Module-specific detailed docs landing page)
    - `new_module/docs/technical_overview.md`
    - `new_module/docs/tutorials/index.md`
    - `new_module/docs/tutorials/example_tutorial.md`
- Familiarity with basic Git operations and navigating directories in a terminal.

## 2. Goal

By the end of this tutorial, you will be able to:

- Create the necessary directory structure within the `documentation` module for `new_module`.
- Copy and adapt `new_module`'s documentation files into the Docusaurus site, adding appropriate frontmatter.
- Add `new_module` to the sidebar navigation in `documentation/sidebars.js`.
- View `new_module`'s documentation rendered in the local Docusaurus development server.

## 3. Steps

### Step 1: Create Directory Structure for `new_module`

Navigate to the `documentation/docs/modules/` directory and create the following structure for `new_module`:

```bash
cd documentation/docs/modules
mkdir -p new_module/docs/tutorials
# Create .gitkeep files if desired to commit empty directories initially
# touch new_module/.gitkeep
# touch new_module/docs/.gitkeep
# touch new_module/docs/tutorials/.gitkeep
```

### Step 2: Copy and Adapt Root-Level Module Files

For each standard file (`README.md`, `API_SPECIFICATION.md`, etc.) from `new_module/`:

1.  **Copy** the file from `../../../../new_module/FILENAME.md` to `documentation/docs/modules/new_module/RENAMED_OR_SAME_FILENAME.md`.
    *   `README.md` should be copied to `index.md` (e.g., `cp ../../../../new_module/README.md ./new_module/index.md`).
    *   Other files usually keep their names (e.g., `cp ../../../../new_module/API_SPECIFICATION.md ./new_module/api_specification.md`).
2.  **Edit** the copied file in `documentation/docs/modules/new_module/`:
    *   Add Docusaurus **frontmatter** at the very top. For example, for `index.md`:
        ```markdown
        ---
        sidebar_label: 'New Module Name' # (e.g., New Module)
        title: 'New Module Overview'
        slug: /modules/new_module # (Ensures a clean URL)
        ---
        ```
        For `api_specification.md`:
        ```markdown
        ---
        sidebar_label: 'API Specification'
        title: 'New Module - API Specification'
        ---
        ```
        Adjust `sidebar_label` and `title` appropriately for each file.
    *   **Update internal links** to point to the new Docusaurus paths. For example, a link in `index.md` like `[API Specification](API_SPECIFICATION.md)` should become `[API Specification](./api_specification.md)`.

### Step 3: Copy and Adapt Module's `docs/` Content

For files within `new_module/docs/` (like `index.md`, `technical_overview.md`, and tutorial files):

1.  **Copy** files from `../../../../new_module/docs/` to `documentation/docs/modules/new_module/docs/`.
    *   e.g., `cp ../../../../new_module/docs/technical_overview.md ./new_module/docs/technical_overview.md`
    *   Copy tutorial files into `documentation/docs/modules/new_module/docs/tutorials/`.
2.  **Edit** each copied file:
    *   Add Docusaurus **frontmatter**. For `technical_overview.md`:
        ```markdown
        ---
        sidebar_label: 'Technical Overview'
        title: 'New Module - Technical Overview'
        ---
        ```
    *   **Update internal links**. Links like `[API Specification](../../API_SPECIFICATION.md)` might become `[API Specification](../../api_specification.md)` or `[Tutorials Index](./tutorials/)` would be `[Tutorials Index](./tutorials/index.md)` (if you create an explicit index for tutorials).

### Step 4: Update `sidebars.js`

Open `documentation/sidebars.js`. Locate the `items` array under the main 'Modules' category. Add a new entry for `new_module` following the pattern of existing modules:

```javascript
// ... inside tutorialSidebar -> Modules -> items array
{
  type: 'category',
  label: 'New Module', // Display name in sidebar
  link: {type: 'doc', id: 'modules/new_module/index'}, // Links to the module's main page
  items: [
    'modules/new_module/api_specification',
    'modules/new_module/mcp_tool_specification',
    'modules/new_module/usage_examples',
    'modules/new_module/changelog',
    'modules/new_module/security',
    {
      type: 'category',
      label: 'Detailed Docs & Tutorials',
      link: {type: 'doc', id: 'modules/new_module/docs/index'},
      items: [
        'modules/new_module/docs/technical_overview',
        {
          type: 'category',
          label: 'Tutorials',
          link: {type: 'doc', id: 'modules/new_module/docs/tutorials/index'},
          items: [
            'modules/new_module/docs/tutorials/example_tutorial',
            // Add other tutorial IDs here
          ]
        }
      ]
    }
  ]
},
// ... other modules
```
Ensure the paths in `id:` fields match the file paths within `documentation/docs/` (without the `.md` extension, and Docusaurus automatically resolves `index` in a directory if linked to the directory path).

### Step 5: Verify Locally

1.  Navigate to the `documentation` module root if not already there:
    ```bash
    cd path/to/codomyrmex/documentation
    ```
2.  Start the development server:
    ```bash
    npm run start
    ```
3.  Open your browser to `http://localhost:3000` (or the port shown in the terminal).
4.  Check if "New Module" appears in the sidebar under "Modules".
5.  Navigate through all the pages for `new_module`, verifying content and checking for broken links.

## 4. Understanding the Results

If successful, `new_module`'s documentation will be fully integrated into the Codomyrmex documentation website. All its standard documentation pages and detailed docs/tutorials will be accessible through the sidebar navigation and correctly rendered.

## 5. Troubleshooting

- **Broken Links**: Double-check all relative links in your Markdown files and in `sidebars.js`. Pay attention to `../` and ensure paths align with the Docusaurus structure.
- **Module Not in Sidebar**: Ensure `sidebars.js` is saved and the structure is correct. Check for typos in labels or IDs.
- **Page Not Found (404)**: Verify the `id` in `sidebars.js` matches the actual file path in `documentation/docs/` (e.g., `modules/new_module/docs/technical_overview` for `documentation/docs/modules/new_module/docs/technical_overview.md`). Also check the `slug` in frontmatter if used.
- **Frontmatter Issues**: Ensure frontmatter is valid YAML and at the very beginning of the file.

## 6. Next Steps

Congratulations! You've added a new module's documentation.

- Commit your changes in the `documentation` module to Git.
- If this is a new module, ensure the original documentation files in `new_module/` are also committed.
- Consider if any placeholder content in the copied templates needs to be filled out for `new_module`. 