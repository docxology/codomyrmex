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
    - `project/`: Markdown files related to the overall Codomyrmex project (e.g., Contributing, Code of Conduct, License).
    - `modules/`: This directory is intended to hold documentation sourced from individual Codomyrmex modules. The aggregation process might involve a build step or script to copy/link relevant files here.
    - `development/`: Documentation related to development processes, architecture, and environment setup.
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

To use the script, navigate to the Codomyrmex project root and run commands like:
```bash
python documentation/documentation_website.py [action] [--pm <npm|yarn>]
```

**Key Actions defined in `documentation_website.py`:**
*   **No action (default - `full_cycle`)**: Performs a sequence: `checkenv`, `install`, `build`, `assess` (opens browser), and `serve`.
*   `checkenv`: Checks for Node.js and npm/yarn.
*   `install`: Installs Docusaurus dependencies (`npm install` or `yarn install`).
*   `start`: Runs the Docusaurus development server (`npm run start` or `yarn start`).
*   `build`: Builds the static Docusaurus site (`npm run build` or `yarn build`).
*   `serve`: Serves the previously built static site from `documentation/build/` (`npm run serve` or `yarn serve`).
*   `assess`: Opens the default site URL (`http://localhost:3000`) in a browser and prints an assessment checklist (expects a server to be running).

**Package Manager Option:**
*   Use the `--pm` argument to specify `npm` or `yarn`. If omitted, `npm` is the default.
    ```bash
    python documentation/documentation_website.py build --pm yarn
    ```
Refer to the script's internal help (`python documentation/documentation_website.py --help`) for the most up-to-date list of actions and options.

## Integrating Module Documentation

A key function of this module is to aggregate and present documentation from other Codomyrmex modules. The strategy for this typically involves:

1.  **Consistent Documentation in Modules**: Each Codomyrmex module should maintain its own documentation (e.g., `README.md`, `API_SPECIFICATION.md`, `MCP_TOOL_SPECIFICATION.md`, and potentially a `docs/` subdirectory with more detailed guides like `technical_overview.md`).
2.  **Aggregation Mechanism**: A process (manual, scripted via `documentation_website.py`, or using Docusaurus features/plugins) will be needed to gather these Markdown files. The target location within this module is typically `documentation/docs/modules/<module-name>/`.
    - This might involve copying files or creating symlinks during a pre-build step.
    - The `documentation_website.py` script may be enhanced to automate parts of this aggregation.
3.  **Sidebar Configuration**: The `documentation/sidebars.js` file must be updated to include links to the aggregated module documentation, creating a structured and navigable hierarchy.
4.  **Cross-Module Linking**: Ensure links between module documents and the main project documentation work correctly.

The specific implementation of this aggregation should be detailed in this module's `docs/technical_overview.md` or a dedicated guide within the documentation site itself.

## Further Information

- For specific API or tool specifications *of this documentation module itself* (e.g., related to the `documentation_website.py` script or any future automation tools built herein), refer to:
    - [API Specification](API_SPECIFICATION.md) (Placeholder, for any direct Python APIs this module might expose)
    - [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md) (Details MCP tools like `trigger_documentation_build`)
- [Usage Examples](USAGE_EXAMPLES.md): Examples for using any specific tools or scripts within this module.
- [Detailed Documentation for this module](./docs/index.md): If this module has its own specific detailed guides beyond this README.
- [Changelog](CHANGELOG.md): Tracks changes to the documentation module itself.
- [Security Policy](SECURITY.md): Security considerations for this module (e.g., related to running build scripts or serving content).

(Note: The `API_SPECIFICATION.md`, `USAGE_EXAMPLES.md`, etc., in this directory pertain to the `documentation` module's own components, not the overall Codomyrmex project documentation content, unless specifically about tools for managing that content.) 