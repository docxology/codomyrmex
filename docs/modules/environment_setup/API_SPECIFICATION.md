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

### Function 2: `check_and_setup_env_vars(repo_root: str | None = None, required: list[str] | None = None, optional: list[str] | None = None) -> list[str]`

- **Source**: `environment_setup.env_checker.check_and_setup_env_vars`
- **Description**: Loads environment variables from a `.env` file, then reports which required variables are missing. With `repo_root` it loads `<repo_root>/.env` when that file exists (a missing file is only logged at debug level); without it, `dotenv.load_dotenv()` searches for a `.env` file from the current directory upwards. Missing required variables are logged as a warning; the function does not print setup instructions or exit.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `repo_root` (str, optional): Directory containing the `.env` file.
    - `required` (list[str], optional): Environment variables that must be present.
    - `optional` (list[str], optional): Environment variables that may be absent; accepted for documentation and not checked.
- **Request Body**: N/A
- **Returns/Response**: `list[str]` of required variable names that are not set (empty when all are present).
  - **Side Effects**: Loads variables from the `.env` file into the current process's environment.
- **Events Emitted**: N/A

### Function 3: `validate_python_version(min_version: str = "3.10") -> bool`

- **Source**: `environment_setup.env_checker.validate_python_version`
- **Description**: Checks that the running Python version is at least `min_version`, comparing dotted numeric components (for example `"3.11"`).
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `min_version` (str, optional): Minimum version as dotted numbers, without specifiers such as `>=` (default: `"3.10"`).
- **Request Body**: N/A
- **Returns/Response**: `bool`
    - `True` if the current Python version is at least `min_version`
    - `False` otherwise. If `min_version` is not in dotted-number form, the error is logged and the result is whether Python is at least 3.10.
- **Events Emitted**: N/A

### Function 4: `validate_environment(min_python: str = "3.10") -> ValidationReport`

- **Source**: `environment_setup.env_checker.validate_environment`
- **Description**: Performs comprehensive validation of the Python runtime and core dependencies.
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function: `from codomyrmex.environment_setup import validate_environment`)
- **Parameters/Arguments**:
    - `min_python` (str, optional): Minimum Python version, defaulting to `"3.10"`.
- **Request Body**: N/A
- **Returns/Response**: `ValidationReport` with `valid`, `missing_items`, and `details` fields.
- **Events Emitted**: N/A

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
