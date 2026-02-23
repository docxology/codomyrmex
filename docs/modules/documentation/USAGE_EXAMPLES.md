# Documentation - Usage Examples

This document provides usage examples for the tools and scripts within the `documentation` module, primarily focusing on the `documentation_website.py` helper script.

<!-- TODO: Ensure all examples are tested and accurately reflect the script's capabilities and options as defined in `documentation_website.py --help` and the main README.md. -->

## Example 1: Starting the Docusaurus Development Server

This example shows how to start the local Docusaurus development server, which provides live reloading as you make changes to documentation files.

```bash
# Navigate to the Codomyrmex project root directory
# cd /path/to/codomyrmex

# Run the 'start' action using the documentation_website.py script
python documentation/documentation_website.py start

# To use yarn instead of the default npm:
# python documentation/documentation_website.py start --pm yarn
```

### Expected Outcome

- The script will first check for Node.js and the selected package manager (npm or yarn).
- It will then navigate to the `documentation/` directory and execute `npm run start` (or `yarn start`).
- You should see output from Docusaurus indicating the server is running, typically on `http://localhost:3000`.
- Your default web browser might open automatically to this URL.
- The server will continue running; press `Ctrl+C` in the terminal to stop it.

## Example 2: Building the Static Documentation Site

This example demonstrates how to build the static HTML, CSS, and JavaScript assets for the documentation site, suitable for deployment.

```bash
# Navigate to the Codomyrmex project root directory
# cd /path/to/codomyrmex

# Run the 'build' action using the documentation_website.py script
python documentation/documentation_website.py build

# To use yarn:
# python documentation/documentation_website.py build --pm yarn
```

### Expected Outcome

- The script will check the environment and then execute `npm run build` (or `yarn build`) within the `documentation/` directory.
- Docusaurus will generate the static site into the `documentation/build/` directory.
- You will see log output indicating the progress and completion of the build process.

## Example 3: Checking the Documentation Environment

This example shows how to use the script to check if Node.js and npm/yarn are installed and accessible.

```bash
# Navigate to the Codomyrmex project root directory
# cd /path/to/codomyrmex

# Run the 'checkenv' action
python documentation/documentation_website.py checkenv
```

### Expected Outcome

- The script will output information about the detected versions of Node.js, npm, and yarn (if found).
- It will indicate if any of the required tools are missing.

## Example 4: Full Cycle (Install, Build, Assess, Serve)

This example shows how to run the default action of `documentation_website.py` which performs a full sequence: checks environment, installs dependencies, builds the site, opens it in a browser (assess), and then serves it locally.

```bash
# Navigate to the Codomyrmex project root directory
# cd /path/to/codomyrmex

# Run the script with no specific action (defaults to 'full_cycle')
python documentation/documentation_website.py

# To use yarn:
# python documentation/documentation_website.py --pm yarn
```

### Expected Outcome

- The script will perform the following sequence:
    1. `checkenv`: Verifies Node.js and package manager.
    2. `install`: Runs `npm install` or `yarn install` in `documentation/`.
    3. `build`: Runs `npm run build` or `yarn build` in `documentation/`.
    4. `assess`: Opens `http://localhost:3000` (or the configured Docusaurus port) in your browser.
    5. `serve`: Starts serving the built site from `documentation/build/`.
- You should see logs for each step and end up with the built site being served and opened in your browser.

## Common Pitfalls & Troubleshooting

- **Issue**: `ModuleNotFoundError: No module named 'codomyrmex.logging_monitoring'` when running `documentation_website.py`.
  - **Solution**: Ensure you have installed the main Codomyrmex project dependencies via `uv sync` in your Python environment, as `documentation_website.py` attempts to use the project's logging module.

- **Issue**: `npm` or `yarn` commands fail (e.g., `npm ERR! ...`).
  - **Solution**:
    - Ensure Node.js and the respective package manager (npm or yarn) are correctly installed and in your system's PATH. Refer to `environment_setup/README.md`.
    - Check the specific error message. It might indicate missing peer dependencies for Docusaurus or network issues during package download.
    - Try deleting `documentation/node_modules/` and `documentation/package-lock.json` (or `yarn.lock`) and re-running the install command (e.g., `python documentation/documentation_website.py install`).

- **Issue**: Port `3000` is already in use when trying to start or serve.
  - **Solution**: Docusaurus (or the `serve` package) might try to use another port if 3000 is busy. Check the terminal output for the actual URL. You can often configure the port Docusaurus uses via command-line flags or its configuration, though the `documentation_website.py` script does not currently pass these through. You might need to run the `npm run start -- --port <new_port>` command manually in the `documentation/` directory if this is a persistent issue.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
