# Environment Setup for Codomyrmex Project

This first part of this document outlines the general steps to set up the development environment for the **entire Codomyrmex project**. For details specific to the `environment_setup` module itself, see the sections further below starting with "## Environment Setup Module Overview".

## I. General Project Development Environment Setup

**(Note: These instructions cover the setup for the overall Codomyrmex project. Consider moving this section to the main project `README.md` for better organization.)**

### Prerequisites

- Python 3.9 or higher
- `pip` (Python package installer)
- `git`
- Node.js (Version 18.0 or higher, for `documentation` module)
- npm or yarn (for `documentation` module)

### Setup Instructions

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd codomyrmex
    ```

2.  **Create and Activate a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Python Dependencies:**
    The project dependencies, including the `cased/kit` toolkit and `python-dotenv`, are listed in the `requirements.txt` file at the root of the project.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Keys (for LLM features):**
    If you plan to use features interacting with Large Language Models (e.g., via `ai_code_editing` or `cased/kit`), you will need API keys for services like OpenAI, Anthropic, or Google Cloud.
    Create a `.env` file in the project root (`codomyrmex/.env`) and add your keys:
    ```env
    OPENAI_API_KEY="sk-..."
    ANTHROPIC_API_KEY="sk-ant-..."
    GOOGLE_API_KEY="AIzaSy..."
    # Add other environment-specific variables here
    ```
    The `python-dotenv` library (installed via `requirements.txt`) will load these variables. The `env_checker.py` script in the `environment_setup` module can help verify this setup.

5.  **Graphviz (Optional for Dependency Visualization):**
    Some modules or tools (like `cased/kit` for dependency graphs) may require Graphviz.
    -   Install the Graphviz system package: [graphviz.org/download/](https://graphviz.org/download/).
    -   Install the Python bindings: `pip install graphviz` (ensure it's in the root `requirements.txt` if widely used).

6.  **Setup for the `documentation` Module (Docusaurus):**
    The project documentation website is built using Docusaurus.
    -   Navigate to the `documentation` directory: `cd documentation`
    -   Install Node.js dependencies: `npm install` (or `yarn install`)
    -   Refer to `documentation/README.md` for commands to run the dev server or build the site.

---

## II. `environment_setup` Module Overview

This module is dedicated to ensuring a smooth and consistent setup experience for developers working on the Codomyrmex project. It provides instructions, scripts (like `env_checker.py`), and guidance for installing prerequisites, configuring dependencies, and managing environment variables (such as API keys). Its primary aim is to simplify the initial onboarding process and to help maintain a stable development environment across different systems.

## Key Components of the `environment_setup` Module

- **`env_checker.py` Script**: A Python script containing utility functions:
    - `ensure_dependencies_installed()`: Verifies the presence of crucial project dependencies (like `cased/kit`, `python-dotenv`) by attempting to import them. It provides instructional messages if dependencies are missing, guiding the user to install them via the root `requirements.txt`.
    - `check_and_setup_env_vars(repo_root_path: str)`: Checks for a `.env` file in the specified repository root. If missing, it guides the user on creating one with the necessary API key placeholders (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`).
- **Setup Instructions & Documentation**: This `README.md` file for the `environment_setup` module itself.
- **Virtual Environment Guidance**: Reinforces the use of virtual environments (e.g., Python's `venv`).
- **Dependency Manifests**: Primarily relies on the root `requirements.txt`. This module's own `requirements.txt` is for any dependencies specific to `env_checker.py` itself, if they were not in the root (currently, they are expected to be in the root).
- **`.env` File Management**: Provides guidance (via `env_checker.py` and documentation) for creating and managing `.env` files for sensitive information.

## Integration Points of the `environment_setup` Module

This module is foundational for all other development activities within Codomyrmex:

- **Provides:**
    - **A Well-Defined Development Environment**: Through its documentation and the `env_checker.py` script, it helps ensure all developers have the necessary tools, Python dependencies (e.g., `cased/kit`, `python-dotenv`), and configurations (e.g., API keys via `.env` files loaded by `python-dotenv`).
    - **`env_checker.py` Utilities** (callable by other scripts or for direct use):
        - `ensure_dependencies_installed()`: Verifies essential project Python dependencies.
        - `check_and_setup_env_vars(repo_root_path: str)`: Validates and guides `.env` file setup for API keys.
    - **Guidance on System Prerequisites**: Information on required system-level tools like Python, pip, git.

- **Consumes:**
    - **Operating System Utilities**: Relies on `python` and `pip` being available on the developer's system.
    - **Project `requirements.txt`**: `env_checker.py` implicitly relies on this file for listing the necessary Python packages that should be installed.
    - **`cased/kit` and `python-dotenv`**: `env_checker.py` specifically checks for the presence of these key libraries.
    - **(Indirectly) All other Codomyrmex modules**: All modules depend on a correctly set up environment. They may directly import and use functions from `env_checker.py` at the beginning of their scripts to validate the environment.

- Refer to the [API Specification](./API_SPECIFICATION.md) (currently a template) and [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) (currently N/A) for detailed programmatic interfaces for this module itself.

## Getting Started with the `environment_setup` Module

The primary way to "use" this module is by following the general project setup instructions (see Part I of this README or the main project README) and by potentially running the `env_checker.py` script to validate your environment.

### Prerequisites for using `env_checker.py`

- Python 3.9+ installed and accessible.
- The Codomyrmex project cloned.

### Running `env_checker.py`

You can run the script directly from the project root to check your setup:

```bash
python environment_setup/env_checker.py
```
This will execute the checks within its `if __name__ == '__main__':` block, which calls `ensure_dependencies_installed()` and `check_and_setup_env_vars()`.

Other scripts or modules within Codomyrmex might import and call these functions directly:
```python
from environment_setup.env_checker import ensure_dependencies_installed, check_and_setup_env_vars
import os

# Early in your script
ensure_dependencies_installed()
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Adjust as needed
check_and_setup_env_vars(project_root)

# ... rest of your script ...
```

### Configuration for this Module

This module itself (`env_checker.py`) does not require external configuration beyond having Python installed. Its behavior is to check for configurations needed by *other* modules (like the `.env` file).

## Development of the `environment_setup` Module

Contributions to this module would typically involve enhancing `env_checker.py` to check for new common dependencies, improve instructional messages, or add more comprehensive environment validation.

### Code Structure

- `README.md`: This file.
- `env_checker.py`: Core Python script with environment checking functions.
- `API_SPECIFICATION.md`: Template for API specs if `env_checker.py` functions were to be formally documented as an API.
- `MCP_TOOL_SPECIFICATION.md`: Currently N/A, as this module doesn't expose MCP tools.
- `requirements.txt`: For any Python dependencies *specific* to `env_checker.py` that are not in the root `requirements.txt` (currently, none expected).
- `docs/`: For more detailed documentation, if needed (e.g., `technical_overview.md`).
- `tests/`: For unit tests for `env_checker.py`.

### Building & Testing

- **Building**: This module consists of Python scripts and does not require a separate build step.
- **Testing**: Unit tests for `env_checker.py` should be developed in the `environment_setup/tests/` directory.
    - Tests would involve mocking `sys.exit`, `os.path.exists`, `importlib` (for import checks), and `builtins.print` to verify correct behavior and output under various conditions (e.g., dependencies missing, `.env` file present/absent).
    - Example test execution (using `pytest` from the project root):
      ```bash
      pytest environment_setup/tests/
      ```
    Refer to `environment_setup/tests/README.md` for specific testing instructions for this module.

## Further Information

- [API Specification](./API_SPECIFICATION.md)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](./USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md) 