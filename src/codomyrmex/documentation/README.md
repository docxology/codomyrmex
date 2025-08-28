# Codomyrmex Documentation Hub

This module is responsible for generating and serving the comprehensive documentation website for the Codomyrmex project.

## Overview

The documentation website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.
It aims to consolidate documentation from all Codomyrmex modules, providing a centralized and easy-to-navigate resource for users and developers.

Key features include:
- Unified documentation for all modules.
- Search functionality.
- Versioning support (to be configured as needed).
- Blog/update sections (can be enabled if desired).

## Structure

The Docusaurus project is structured as follows:

- `docs/`: Contains the Markdown files that form the content of the documentation site. 
    - `intro.md`: The main landing page for the documentation.
    - `project/`: Markdown files related to the overall Codomyrmex project (e.g., general contribution guidelines, code of conduct, license information, overall architecture).
    - `modules/`: This directory is intended to hold documentation sourced from individual Codomyrmex modules. The aggregation process involves copying relevant files (like `README.md`, `API_SPECIFICATION.md`, `docs/technical_overview.md`, `docs/tutorials/*`) into subdirectories named after each module (e.g., `docs/modules/ai_code_editing/`).
    - `development/`: Documentation related to development processes, advanced setup, and specific architectural deep-dives for the project as a whole.
    - `tutorials/`: Project-wide tutorials that may span multiple modules or cover general concepts.
- `src/`: Contains non-documentation files like custom React components (under `src/components/`) or custom CSS (under `src/css/`).
    - `css/custom.css`: For custom styling overrides.
- `static/`: Static assets like images, which will be copied to the root of the build output.
- `docusaurus.config.js`: The main Docusaurus configuration file. Controls site metadata, plugins, themes, and presets.
- `sidebars.js`: Defines the structure and content of the navigation sidebar(s).
- `package.json`: Node.js project manifest. Lists dependencies (Docusaurus, React, etc.) and scripts (`start`, `build`, `serve`).

## Getting Started (Running Locally)

### Prerequisites

- **Node.js**: Version 18.0 or higher is recommended. Check Docusaurus documentation for current specific version compatibility if issues arise.
- **npm or yarn**: A Node.js package manager. `npm` usually comes with Node.js. `yarn` can be installed separately if preferred.

Refer to the main `environment_setup/README.md` in the Codomyrmex project root for general instructions on installing Node.js.

### Installation

1.  Navigate to the `documentation` directory within the Codomyrmex project:
    ```bash
    cd documentation
    ```
2.  Install the Node.js dependencies listed in `package.json`:
    ```bash
    npm install
    # OR, if you prefer yarn:
    # yarn install
    ```

### Running the Development Server

To start the Docusaurus local development server with live reloading:

1.  Ensure you are in the `documentation` directory.
2.  Run the start script:
    ```bash
    npm run start
    # OR, with yarn:
    # yarn start
    ```
This command typically starts the server on `http://localhost:3000` and opens it in your default web browser. Changes to Markdown files or Docusaurus configuration will usually reflect live.

### Building the Static Site

To generate a static build of the website, suitable for deployment to a hosting service:

1.  Ensure you are in the `documentation` directory.
2.  Run the build script:
    ```bash
    npm run build
    # OR, with yarn:
    # yarn build
    ```
This command generates the static HTML, CSS, and JavaScript assets into the `documentation/build` directory.

### Serving the Static Build Locally

After building the site, you can serve it locally to preview the production version:

1. Ensure you have built the site (see above).
2. Run the serve script:
    ```bash
    npm run serve
    # OR, with yarn:
    # yarn serve
    ```
This usually serves the site from `http://localhost:3000` (or another port if 3000 is in use).

### Using the `documentation_website.py` Helper Script

A Python script `documentation_website.py` is provided within this `documentation` module to streamline common operations related to the Docusaurus site. This script requires Python to be installed and accessible in your environment. It also attempts to use `codomyrmex.logging_monitoring` for enhanced logging, so ensure the main project Python dependencies are installed (see root `requirements.txt`).

The script currently supports actions like checking the environment (`checkenv`), installing dependencies (`install`), starting the dev server (`start`), building the static site (`build`), and serving the build (`serve`). It can also attempt to open the site in a browser (`assess`).

To use the script, navigate to the Codomyrmex project root and run commands like:
```bash
python documentation/documentation_website.py [action] [--pm <npm|yarn>]
```

**Key Actions defined in `documentation_website.py`:**
*   **No action (default - `full_cycle`)**: Performs a sequence: `checkenv`, `install`, `build`, `assess` (opens browser), and `serve`.
*   `checkenv`: Checks for Node.js and npm/yarn.
*   `install`: Installs Docusaurus dependencies (`npm install` or `yarn install` in the `documentation/` directory).
*   `start`: Runs the Docusaurus development server (`npm run start` or `yarn start` from `documentation/`).
*   `build`: Builds the static Docusaurus site (`npm run build` or `yarn build` from `documentation/`).
*   `serve`: Serves the previously built static site from `documentation/build/` (`npm run serve` or `yarn serve` from `documentation/`).
*   `assess`: Opens the default site URL (`http://localhost:3000`) in a browser and prints an assessment checklist (expects a server to be running).
*   `aggregate_docs`: (Conceptual, future enhancement) This action would automate copying documentation from individual modules into the `documentation/docs/modules/` directory. Currently, this aggregation is a manual or semi-automated step.

**Package Manager Option:**
*   Use the `--pm` argument to specify `npm` or `yarn`. If omitted, `npm` is the default.
    ```bash
    python documentation/documentation_website.py build --pm yarn
    ```
Refer to the script's internal help (`python documentation/documentation_website.py --help`) for the most up-to-date list of actions and options.

## Integrating Module Documentation

A key function of this module is to aggregate and present documentation from other Codomyrmex modules. The current strategy involves:

1.  **Consistent Documentation in Modules**: Each Codomyrmex module (e.g., `ai_code_editing`, `data_visualization`) MUST maintain its own documentation. This typically includes:
    *   `README.md` (module overview, basic usage)
    *   `API_SPECIFICATION.md` (for any Python APIs)
    *   `MCP_TOOL_SPECIFICATION.md` (for Model Context Protocol tools)
    *   `docs/technical_overview.md` (detailed architecture, design decisions)
    *   `docs/tutorials/*.md` (specific tutorials for the module's features)
    *   Other relevant files like `SECURITY.md`, `CHANGELOG.md`, `USAGE_EXAMPLES.md`.
2.  **Aggregation/Copying Mechanism**:
    *   **Current Approach**: Relevant Markdown files from each module are manually or script-assisted (e.g., using a custom script or future enhancements to `documentation_website.py`) copied into a corresponding subdirectory within `documentation/docs/modules/`. For example, `ai_code_editing/README.md` would be copied to `documentation/docs/modules/ai_code_editing/README.md`.
    *   The `documentation_website.py` script may be enhanced in the future with an `aggregate_docs` action to automate this.
3.  **Sidebar Configuration**: The `documentation/sidebars.js` file must be manually updated to include links to the aggregated module documentation, creating a structured and navigable hierarchy. This ensures that all copied module documents appear in the website's navigation.
4.  **Cross-Module Linking**: When writing documentation, use relative Markdown links. Docusaurus will resolve these correctly if the file structure is maintained during aggregation. For example, a link from `ai_code_editing/docs/technical_overview.md` to `ai_code_editing/README.md` should work as `../README.md` within the module, and Docusaurus should handle this correctly once both are in `documentation/docs/modules/ai_code_editing/`.

The specific implementation details of aggregation and any automation scripts should be further detailed in this module's `docs/technical_overview.md` or a dedicated guide within the documentation site itself (e.g., under `docs/development/DocumentationPipeline.md`).

## Project Documentation Structure (High-Level)

The documentation website aims for the following general structure:

- **Introduction**: Landing page with an overview of Codomyrmex.
- **Getting Started**: Essential setup, installation, and basic usage guides for the project.
- **Project Information**:
    - Overall Architecture
    - Contribution Guidelines (Code & Documentation)
    - Code of Conduct
    - License
- **Modules**: Dedicated sections for each Codomyrmex module, providing:
    - Overview (from module `README.md`)
    - API Specifications (if applicable)
    - MCP Tool Specifications (if applicable)
    - Technical Overviews
    - Tutorials
    - Usage Examples
    - Security Information
    - Changelogs
- **Tutorials**: Project-wide tutorials that cover broader concepts or workflows involving multiple modules.
- **Development Guides**: Information for developers contributing to Codomyrmex, including:
    - Advanced Environment Setup
    - Coding Standards
    - Testing Strategies
    - Documentation Pipeline (how this site is built and maintained)
- **API Reference (Future)**: Potentially auto-generated API documentation for Python modules.
- **Blog/Updates (Optional)**: For project news and announcements.

## Contributing to Documentation

Contributions to the Codomyrmex documentation are vital and highly encouraged! The process generally involves:

1.  **Identify the Correct Location**:
    *   **Module-Specific Content**: For documentation directly related to a single Codomyrmex module (e.g., `ai_code_editing`'s features, API, or tutorials), edits MUST be made to the Markdown files (`README.md`, `API_SPECIFICATION.md`, `docs/*`, etc.) located *within that module's own directory* (e.g., `ai_code_editing/docs/technical_overview.md`). **Do not directly edit files under `documentation/docs/modules/` as these are copies and your changes will be overwritten.**
    *   **Project-Wide Content**: For documentation that spans the entire project (e.g., overall architecture, top-level tutorials, general contribution guidelines, Code of Conduct), edits should be made to files within the `documentation` module itself, typically under `documentation/docs/project/`, `documentation/docs/development/`, or `documentation/docs/tutorials/`.
    *   **Docusaurus Site Configuration**: Changes to the website's structure, navigation (sidebars), overall appearance, or build process involve editing files like `docusaurus.config.js`, `sidebars.js`, or `src/css/custom.css` within this `documentation` module.
2.  **Make Your Edits**: Write clear, concise, and accurate documentation. Follow existing style and formatting.
3.  **Aggregation (If editing module-specific docs)**: After making changes to module-local documentation, the aggregation mechanism (currently manual copying or future `documentation_website.py aggregate_docs` action) needs to be performed to bring your updated files into the `documentation/docs/modules/` directory. If `sidebars.js` needs changes (e.g., new tutorial file added), edit `documentation/sidebars.js` accordingly.
4.  **Testing Locally**:
    *   Navigate to the `documentation` directory: `cd documentation`
    *   Install dependencies if you haven't already: `npm install` (or `yarn install`)
    *   Run the Docusaurus development server: `npm run start` (or `yarn start`, or `python ../documentation_website.py start`)
    *   Preview your changes in your browser (usually `http://localhost:3000`). Ensure content renders correctly, formatting is good, and all links work.
5.  **Submitting Changes**: Follow the general Codomyrmex project contribution guidelines (see main `CONTRIBUTING.md` in the project root) for committing your changes and submitting a pull request.

Detailed guidelines on documentation style, voice, use of Markdown features, and specific conventions for structuring content will be maintained within the documentation site itself, under `docs/project/CONTRIBUTING_TO_DOCUMENTATION.md`.

## Further Information

- For specific API or tool specifications *of this documentation module itself* (e.g., related to the `documentation_website.py` script or any future automation tools built herein), refer to:
    - [API Specification](API_SPECIFICATION.md) (Details any Python APIs this module might expose, e.g., for `documentation_website.py`)
    - [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) (Details MCP tools like `trigger_documentation_build` if implemented)
- [Usage Examples](USAGE_EXAMPLES.md): Examples for using any specific tools or scripts within this `documentation` module.
- [Detailed Documentation for this module](./docs/index.md): Specific guides for the `documentation` module itself (e.g., technical overview, how to manage the Docusaurus setup).
- [Changelog](CHANGELOG.md): Tracks changes to the `documentation` module's infrastructure and scripts.
- [Security Policy](SECURITY.md): Security considerations for this module (e.g., related to build scripts, dependencies, or serving content).

(Note: The `API_SPECIFICATION.md`, `USAGE_EXAMPLES.md`, etc., in this directory pertain to the `documentation` module's own components, not the overall Codomyrmex project documentation content, unless specifically about tools for managing that content.) 