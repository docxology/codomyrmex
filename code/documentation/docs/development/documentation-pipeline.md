---
sidebar_label: Documentation Pipeline
---

# Documentation Pipeline

This document describes the process for building, maintaining, and deploying the Codomyrmex project documentation website, which is powered by Docusaurus.

## Overview

The documentation pipeline involves several key stages:

1.  **Content Creation & Updates**: Documentation is written in Markdown within individual modules and in the central `documentation` module.
2.  **Content Aggregation**: Module-specific documentation is copied into the `documentation/docs/modules/` directory.
3.  **Docusaurus Build**: Docusaurus processes all Markdown files, configurations, and assets to generate a static HTML website.
4.  **Testing & Preview**: The site is tested locally for correctness, working links, and visual appearance.
5.  **Deployment**: The static site is deployed to a web server or hosting platform (e.g., GitHub Pages).

## 1. Content Creation & Updates

-   **Module-Specific Docs**: Reside within each module (e.g., `ai_code_editing/README.md`, `ai_code_editing/docs/technical_overview.md`). Contributors edit these files directly in the respective module directories.
-   **Project-Wide Docs**: Reside within `documentation/docs/` (e.g., `documentation/docs/project/architecture.md`, `documentation/docs/tutorials/some_tutorial.md`). Contributors edit these directly.
-   **Guidelines**: Follow the guidelines in `documentation/docs/project/CONTRIBUTING_TO_DOCUMENTATION.md`.

## 2. Content Aggregation

This is a crucial step to bring all documentation into the Docusaurus build process.

-   **Source**: Markdown files from each individual Codomyrmex module (e.g., `ai_code_editing/README.md`, `ai_code_editing/API_SPECIFICATION.md`, `ai_code_editing/docs/technical_overview.md`, `ai_code_editing/docs/tutorials/*`, etc.).
-   **Destination**: These files are copied into a corresponding subdirectory under `documentation/docs/modules/`. For example:
    -   `ai_code_editing/README.md` &rarr; `documentation/docs/modules/ai_code_editing/README.md`
    -   `ai_code_editing/docs/technical_overview.md` &rarr; `documentation/docs/modules/ai_code_editing/docs/technical_overview.md`
    -   `ai_code_editing/docs/tutorials/my_tutorial.md` &rarr; `documentation/docs/modules/ai_code_editing/docs/tutorials/my_tutorial.md`
-   **Current Method**: This process is currently **manual or semi-automated**. Developers need to ensure that updated documentation from modules is copied over before a full documentation build meant for deployment.
-   **Future Enhancements**: The `documentation/documentation_website.py` script has a placeholder concept for an `aggregate_docs` action. This action could be implemented to automate the copying process based on a manifest or conventions.
-   **Sidebar Updates**: After aggregation, `documentation/sidebars.js` must be manually checked and updated if new files (especially tutorials) are added or removed, to ensure they appear correctly in the navigation.

## 3. Docusaurus Build Process

-   **Command**: `npm run build` (or `yarn build`) executed from the `documentation/` directory.
    -   This can also be invoked via `python documentation_website.py build` from the project root.
-   **Input**: All files in `documentation/docs/`, `documentation/src/`, `documentation/static/`, `docusaurus.config.js`, `sidebars.js`, and `package.json`.
-   **Output**: A static website in the `documentation/build/` directory.
-   **Key Steps by Docusaurus**:
    -   Parses `docusaurus.config.js` for site settings, theme, plugins.
    -   Reads `sidebars.js` to understand navigation structure.
    -   Processes all `.md` and `.mdx` files in `documentation/docs/`, converting them to HTML.
    -   Resolves internal links and processes assets.
    -   Applies styling from `documentation/src/css/custom.css` and the theme.
    -   Copies static assets from `documentation/static/` to the build output.

## 4. Testing & Preview

-   **Local Development Server**: `npm run start` (or `yarn start`) from the `documentation/` directory.
    -   Accessible at `http://localhost:3000` by default.
    -   Provides live reloading as you edit Markdown files or configurations.
    -   **Essential for**: Previewing changes, checking formatting, testing navigation, and verifying internal links within the scope of currently aggregated files.
-   **Local Build Serve**: `npm run serve` (or `yarn serve`) from `documentation/` after running a build.
    -   Serves the content of `documentation/build/`.
    -   Useful for a final check of the production build before deployment.
-   **Link Checking**: Manually verify links. Consider using a tool like `lychee-link-checker` or a Docusaurus plugin for automated link checking, especially before deployment.

## 5. Deployment

-   **Target Platform**: The primary target for deployment is GitHub Pages.
-   **Configuration for GitHub Pages** (in `docusaurus.config.js`):
    -   `url`: `https://ActiveInference.github.io`
    -   `baseUrl`: `/codomyrmex/`
    -   `organizationName`: `ActiveInference`
    -   `projectName`: `codomyrmex`
-   **Deployment Method**: Docusaurus provides a command for easy deployment to GitHub Pages:
    ```bash
    # Ensure GIT_USER is set if deploying to a different user/org repo
    # Example: GIT_USER=<YourGitHubUsername> npm run deploy
    
    npm run deploy
    # OR
    # yarn deploy
    ```
    This command typically builds the site and pushes the contents of the `build` directory to the `gh-pages` branch of your repository, from which GitHub Pages serves the site.
-   **CI/CD Automation (Future)**: Setting up a GitHub Actions workflow to automatically build and deploy the documentation upon merges to the `main` branch (or a specific `docs` branch) is highly recommended for production. This workflow would typically:
    1.  Checkout the code.
    2.  Set up Node.js.
    3.  (Crucially) Run the content aggregation step (once automated).
    4.  Install Docusaurus dependencies (`npm ci`).
    5.  Build the Docusaurus site (`npm run build`).
    6.  Deploy to GitHub Pages (e.g., using `peaceiris/actions-gh-pages` or Docusaurus's deploy command).

## Maintaining the Pipeline

-   Keep Docusaurus and its dependencies up-to-date by periodically running `npm outdated` and `npm update` (or yarn equivalents) in the `documentation/` directory, testing thoroughly after updates.
-   Ensure the `documentation_website.py` script is maintained if new Docusaurus commands or project structures emerge.
-   Regularly review and improve the content aggregation process, aiming for full automation.

This pipeline ensures that the Codomyrmex documentation remains current, consistent, and easily accessible. 