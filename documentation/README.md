# Codomyrmex Documentation Hub

This module is responsible for generating and serving the comprehensive documentation website for the Codomyrmex project.

## Overview

The documentation website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.
It aims to consolidate documentation from all Codomyrmex modules, providing a centralized and easy-to-navigate resource for users and developers.

Key features include:
- Unified documentation for all modules.
- Versioning support (to be configured).
- Search functionality.
- Potentially, blog/update sections.

## Structure

- `docs/`: Contains the Markdown files that form the content of the documentation site. 
    - `intro.md`: The main landing page (renamed from `index.md` for Docusaurus convention if `routeBasePath` is `/`).
    - `project/`: Markdown files related to the overall project (Contributing, Code of Conduct, License).
    - `modules/`: This directory will be structured to hold documentation from individual Codomyrmex modules. (This might involve a build step to copy files here).
    - `development/`: Documentation related to development processes, like environment setup.
- `src/`: Contains non-documentation files like custom React components or CSS.
    - `css/custom.css`: Custom styling.
- `static/`: Static assets like images.
- `docusaurus.config.js`: Main Docusaurus configuration file.
- `sidebars.js`: Defines the sidebar structure for navigation.
- `package.json`: Node.js project manifest, including dependencies and scripts for Docusaurus.

## Getting Started (Running Locally)

### Prerequisites

- Node.js (version 18.0 or higher recommended, see `package.json` engines).
- npm or yarn.

Refer to the main `environment_setup/README.md` for instructions on installing Node.js if you haven't already.

### Installation

1.  Navigate to the `documentation` directory:
    ```bash
    cd documentation
    ```
2.  Install dependencies:
    ```bash
    npm install
    # or
    # yarn install
    ```

### Running the Development Server

1.  Start the Docusaurus development server:
    ```bash
    npm run start
    # or
    # yarn start
    ```
    This command starts a local development server (usually on `http://localhost:3000`) and opens up a browser window. Most changes are reflected live without having to restart the server.

### Building the Static Site

To generate a static build of the website (typically for deployment):
```bash
npm run build
# or
# yarn build
```
This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Using the `documentation_website.py` Helper Script

A Python script `documentation_website.py` is provided within this `documentation` module to streamline common operations related to the Docusaurus site. This script requires Python to be installed and accessible in your environment. It also relies on `codomyrmex.logging_monitoring` for logging, so ensure the main project dependencies are installed (see root `requirements.txt`).

To use the script, navigate to the Codomyrmex project root and run:
```bash
python documentation/documentation_website.py [action] [--pm <npm|yarn>]
```

**Key Actions:**
*   **No action (default - `full_cycle`)**: If you run the script without specifying an action, it will perform a full sequence:
    1.  `checkenv`: Check for Node.js and npm/yarn.
    2.  `install`: Install Docusaurus dependencies (using npm by default, or yarn if specified with `--pm yarn`).
    3.  `build`: Build the static Docusaurus site.
    4.  `assess`: Open the built site in your browser and print an assessment checklist to the console.
    5.  `serve`: Serve the built static site (usually on `http://localhost:3000`). This command is blocking and will run until you stop it (Ctrl+C).
*   `checkenv`: Only checks for Node.js and npm/yarn.
*   `install`: Only installs Docusaurus dependencies.
*   `start`: Runs the Docusaurus development server with hot-reloading (equivalent to `npm run start`). This is for development and shows live changes.
*   `build`: Only builds the static Docusaurus site.
*   `serve`: Serves the previously built static site from the `documentation/build/` directory.
*   `assess`: Opens the default site URL (`http://localhost:3000`) in a browser and prints an assessment checklist. This expects a server (either `start` or `serve`) to be running.

**Package Manager:**
*   You can specify the package manager using the `--pm` argument. For example, to use yarn:
    ```bash
    python documentation/documentation_website.py --pm yarn
    # or for a specific action:
    python documentation/documentation_website.py install --pm yarn
    ```
    If `--pm` is not provided, `npm` is used by default.

The script provides logging for each step. If the `codomyrmex.logging_monitoring` module cannot be imported, it will fall back to basic Python logging and print a warning.

## Integrating Module Documentation

A key function of this module is to aggregate documentation from other Codomyrmex modules. The strategy for this will likely involve:
1.  Defining a consistent documentation structure within each module (e.g., `README.md`, `API_SPECIFICATION.md`, `docs/index.md`, `docs/technical_overview.md`).
2.  A build script or Docusaurus plugin configuration that copies or links these Markdown files into the `documentation/docs/modules/<module-name>/` directory before the Docusaurus build process.
3.  Updating `sidebars.js` to correctly reference these aggregated module documents.

## Further Information

- For specific API or tool specifications *of this documentation module itself* (if any), refer to:
    - [API Specification](API_SPECIFICATION.md)
    - [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](USAGE_EXAMPLES.md) for this module.
- [Detailed Documentation for this module](./docs/index.md) (if different from the site landing page).
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

(The files `API_SPECIFICATION.md`, `MCP_TOOL_SPECIFICATION.md`, etc., in this directory should describe the `documentation` module itself, not the entire project's documentation process unless specifically about tools *within* this module for managing documentation.) 