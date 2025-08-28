# Environment Setup Module (`environment_setup`)

For general project development environment setup instructions (covering prerequisites, cloning, virtual environments, Python dependencies, API keys, Docusaurus, linters, and tests for the entire Codomyrmex project), please refer to the **"Getting Started: Development Environment Setup"** section in the [main project README.md](../../README.md).

This document focuses on the specifics of the `environment_setup` module itself.

## `environment_setup` Module Overview

This module is dedicated to ensuring a smooth and consistent setup experience for developers working on the Codomyrmex project. It provides utilities (like `env_checker.py`), helper scripts, and guidance for installing prerequisites, configuring dependencies, and managing environment variables (such as API keys). Its primary aim is to simplify the initial onboarding process and to help maintain a stable development environment across different systems.

## Key Components of the `environment_setup` Module

- **`env_checker.py` Script**: A Python script containing utility functions:
    - `ensure_dependencies_installed()`: Verifies the presence of crucial project dependencies (like `cased/kit`, `python-dotenv`) by attempting to import them. It provides instructional messages if dependencies are missing, guiding the user to install them via the root `requirements.txt`.
    - `check_and_setup_env_vars(repo_root_path: str)`: Checks for a `.env` file in the specified repository root. If missing, it guides the user on creating one with the necessary API key placeholders (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`).
- **Setup Instructions & Documentation**: This `README.md` file for the `environment_setup` module itself.
- **Helper Scripts**: Located in `environment_setup/scripts/`:
    - `setup_dev_env.sh`: Automates common setup tasks for the general project environment.
    - `install_hooks.sh`: Installs project-defined Git hooks.
- **Virtual Environment Guidance**: Reinforces the use of virtual environments (e.g., Python's `venv`) for the overall project.
- **Dependency Manifests**: Primarily relies on the root `requirements.txt`. This module's own `requirements.txt` is for any dependencies specific to `env_checker.py` itself, if they were not in the root (currently, they are expected to be in the root).
- **`.env` File Management**: Provides guidance (via `env_checker.py` and documentation) for creating and managing `.env` files for sensitive information for the overall project.

## Integration Points of the `environment_setup` Module

This module is foundational for all other development activities within Codomyrmex:

- **Provides:**
    - **A Well-Defined Development Environment**: Through its documentation (linking to the main project README for general setup) and the `env_checker.py` script, it helps ensure all developers have the necessary tools, Python dependencies (e.g., `cased/kit`, `python-dotenv`), and configurations (e.g., API keys via `.env` files loaded by `python-dotenv`).
    - **`env_checker.py` Utilities** (callable by other scripts or for direct use):
        - `ensure_dependencies_installed()`: Verifies essential project Python dependencies.
        - `check_and_setup_env_vars(repo_root_path: str)`: Validates and guides `.env` file setup for API keys.
    - **Guidance on System Prerequisites**: Information on required system-level tools like Python, pip, git (primarily covered in the main project README).
    - **Helper Scripts**: `setup_dev_env.sh` and `install_hooks.sh` for general project use.

- **Consumes:**
    - **Operating System Utilities**: Relies on `python` and `pip` being available on the developer's system.
    - **Project `requirements.txt`**: `env_checker.py` implicitly relies on this file for listing the necessary Python packages that should be installed.
    - **`cased/kit` and `python-dotenv`**: `env_checker.py` specifically checks for the presence of these key libraries.
    - **(Indirectly) All other Codomyrmex modules**: All modules depend on a correctly set up environment. They may directly import and use functions from `env_checker.py` at the beginning of their scripts to validate the environment.

- Refer to the [API Specification](./API_SPECIFICATION.md) (currently a template) and [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) (currently N/A) for detailed programmatic interfaces for this module itself.

## Getting Started with the `environment_setup` Module

The primary way to "use" this module (beyond benefiting from its scripts during initial project setup) is by potentially running the `env_checker.py` script to validate your environment, or by other modules importing its utility functions.

### Prerequisites for using `env_checker.py`

- Python 3.9+ installed and accessible.
- The Codomyrmex project cloned.
- Project dependencies installed (see main project README).

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

Contributions to this module would typically involve enhancing `env_checker.py` to check for new common dependencies, improve instructional messages, or add more comprehensive environment validation for the overall project.

### Code Structure

- `README.md`: This file.
- `env_checker.py`: Core Python script with environment checking functions.
- `scripts/`: Contains helper shell scripts for setup (`setup_dev_env.sh`) and Git hook installation (`install_hooks.sh`).
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