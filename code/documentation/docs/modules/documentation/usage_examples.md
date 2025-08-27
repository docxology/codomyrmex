---
sidebar_label: 'Usage Examples'
title: 'Documentation Module - Usage Examples'
---

# Documentation Module - Usage Examples

This section provides usage examples related to the `documentation` module itself, such as managing the documentation build, local development, or specific Docusaurus features relevant to Codomyrmex.

## Example 1: Running the Documentation Site Locally

To view the documentation website on your local machine for development or preview:

1.  Ensure Node.js and npm/yarn are installed (see [Development Setup](../../development/environment-setup.md)).
2.  Navigate to the `documentation` module directory:
    ```bash
    cd documentation
    ```
3.  Install dependencies (if not already done):
    ```bash
    npm install
    ```
4.  Start the development server:
    ```bash
    npm run start
    ```

### Expected Outcome

- A local web server will start (usually on `http://localhost:3000`).
- Your default web browser should open to this address, displaying the Codomyrmex documentation homepage.
- Changes made to Markdown files in `documentation/docs/` or configuration files like `docusaurus.config.js` should auto-reload in the browser.

## Example 2: Building the Static Documentation Site

To create a production-ready static build of the website:

1.  Navigate to the `documentation` module directory:
    ```bash
    cd documentation
    ```
2.  Run the build command:
    ```bash
    npm run build
    ```

### Expected Outcome

- Docusaurus will compile the site into static HTML, CSS, and JavaScript files.
- The output will be placed in the `documentation/build/` directory.
- This `build` directory can then be deployed to any static web hosting service (e.g., GitHub Pages, Netlify, Vercel).

## Example 3: Adding a New Module's Documentation

(This is a conceptual example, actual implementation might involve scripting or manual steps)

To add documentation for a new module named `new_module`:

1.  **Create module doc structure:** Ensure `new_module` has standard doc files (`README.md`, `API_SPECIFICATION.md`, etc.) and a `new_module/docs/` directory with `index.md`, `technical_overview.md`, and `tutorials/`.
2.  **Copy to Docusaurus:** Manually or via a script, copy these files into `documentation/docs/modules/new_module/` and `documentation/docs/modules/new_module/docs/` respectively, adding Docusaurus frontmatter (sidebar_label, title).
3.  **Update Sidebar:** Edit `documentation/sidebars.js` to add `new_module` to the 'Modules' category, linking to `modules/new_module/index` and its sub-pages.

### Expected Outcome

- The `new_module` documentation will appear in the sidebar and be browseable on the Docusaurus site after restarting the local server or rebuilding.

## Common Pitfalls & Troubleshooting

- **Issue**: `npm run start` fails with errors about missing dependencies.
  - **Solution**: Ensure you have run `npm install` in the `documentation` directory.
- **Issue**: Changes to Markdown files are not reflecting in the browser.
  - **Solution**: Check the console output of `npm run start` for any errors. Sometimes a full stop and restart of the server is needed, or there might be a syntax error in the Markdown or frontmatter.
- **Issue**: Sidebar links are broken or new module doesn't appear.
  - **Solution**: Double-check the paths in `sidebars.js` and ensure the corresponding `.md` files exist with correct frontmatter (especially the `id` if manually specified, or that the file path matches the Docusaurus auto-generated ID). 