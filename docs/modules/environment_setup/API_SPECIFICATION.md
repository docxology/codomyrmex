# Environment Setup - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the `environment_setup` module. The API consists of Python functions that can be imported and used by other modules or scripts within the Codomyrmex project to verify and guide the setup of the development environment.

These functions are primarily sourced from the `env_checker.py` script.

## Endpoints / Functions / Interfaces

### Function 1: `ensure_dependencies_installed()`

- **Source**: `environment_setup.env_checker.ensure_dependencies_installed`
- **Description**: Checks if essential Python dependencies for the Codomyrmex project (e.g., `cased`, `dotenv`) are installed by attempting to import them. If a dependency is missing, it prints an instructional message to `stderr` and calls `sys.exit(1)`.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**: None.
- **Request Body**: N/A
- **Returns/Response**: None. 
  - **Side Effects**: Prints messages to `stderr` and may terminate the calling script via `sys.exit(1)` if essential dependencies are missing.
- **Events Emitted**: N/A

### Function 2: `check_and_setup_env_vars(repo_root_path: str)`

- **Source**: `environment_setup.env_checker.check_and_setup_env_vars`
- **Description**: Checks for the existence of a `.env` file at the specified `repo_root_path`.
    - If it exists, it informs the user.
    - If it does not exist, it prints detailed instructions for creating a `.env` file with API key configuration examples for OpenAI, Anthropic, and Google AI providers, then exits with status code 1 to indicate the environment is not fully configured.
    - It attempts to load the `.env` file using `dotenv.load_dotenv()` if the file exists.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `repo_root_path` (str): The absolute path to the root of the Codomyrmex repository where the `.env` file is expected.
- **Request Body**: N/A
- **Returns/Response**: None.
  - **Side Effects**: Prints messages to `stdout` or `stderr`. May call `sys.exit(1)` if the `.env` file is missing after guidance. Attempts to load environment variables from the `.env` file into the current process's environment.
- **Events Emitted**: N/A

### Function 3: `validate_python_version(required: str = ">=3.10") -> bool`

- **Source**: `environment_setup.env_checker.validate_python_version`
- **Description**: Validates that the current Python version meets the specified version requirements using semantic versioning comparison.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `required` (str, optional): Version requirement string using PEP 440 specifiers (default: ">=3.10")
- **Request Body**: N/A
- **Returns/Response**: `bool`
    - `True` if current Python version meets requirements
    - `False` if version requirements are not met or validation fails
- **Events Emitted**: N/A

### Function 4: `validate_environment_completeness(repo_root: str | None = None) -> bool`

- **Source**: `environment_setup.env_checker.validate_environment_completeness`
- **Description**: Performs comprehensive validation of the development environment, checking Python version, dependencies, environment variables, and configuration. This is the primary validation function to call before running Codomyrmex operations.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function: `from codomyrmex.environment_setup.env_checker import validate_environment_completeness`)
- **Parameters/Arguments**:
    - `repo_root` (str | None, optional): The root directory of the repository. If not provided, defaults to the parent directory of the codomyrmex package.
- **Request Body**: N/A
- **Returns/Response**: `bool`
    - `True` if all environment checks pass (dependencies installed, .env file loaded, Python version valid)
    - `False` otherwise
- **Events Emitted**: N/A
- **Note**: This function is not re-exported from `__init__.py`; import it directly from `env_checker`.

### Function 5: `generate_environment_report() -> str`

- **Source**: `environment_setup.env_checker.generate_environment_report`
- **Description**: Generates an environment status report. Currently a placeholder that returns a static string; future implementation will return a detailed report.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function: `from codomyrmex.environment_setup.env_checker import generate_environment_report`)
- **Parameters/Arguments**: None
- **Request Body**: N/A
- **Returns/Response**: `str`
    - Currently returns a placeholder string. Will return a full report once implemented.
- **Events Emitted**: N/A
- **Note**: This function is not re-exported from `__init__.py`; import it directly from `env_checker`.

## Data Models

N/A for these functions.

## Authentication & Authorization

N/A. These are local utility functions.

## Rate Limiting

N/A.

## Versioning

These functions will be versioned as part of the `environment_setup` module, following the overall project's semantic versioning. Changes to function signatures or core behavior will be noted in the module's `CHANGELOG.md`. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
