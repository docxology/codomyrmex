# Testing Environment Setup Module

This document describes how to run tests for the `environment_setup` module, primarily focusing on its `env_checker.py` script.

## Prerequisites

-   Python 3.9+ installed and operational.
-   The Codomyrmex project cloned.
-   A Python virtual environment (`.venv`) created and activated at the project root.
-   `pytest` installed in the virtual environment (it should be, via the root `requirements.txt`).

## Running Tests

The `env_checker.py` script is primarily tested through manual execution and by observing its output under different conditions. Unit tests can be written to cover its internal logic.

### Manual Testing of `env_checker.py`

Execute the script from the project root under various scenarios:

1.  **All dependencies installed, `.env` file exists:**
    ```bash
    # Ensure .venv is active and requirements.txt installed
    # Ensure a dummy .env file exists in project root
    python environment_setup/env_checker.py 
    ```
    *Expected*: Script runs, prints INFO messages about found dependencies and `.env` file, exits successfully.

2.  **Essential Python dependency missing (e.g., `python-dotenv` temporarily uninstalled):**
    ```bash
    # Within .venv:
    # pip uninstall python-dotenv -y 
    python environment_setup/env_checker.py
    # pip install python-dotenv # Reinstall afterwards
    ```
    *Expected*: Script prints ERROR messages about missing `python-dotenv`, provides INSTRUCTION to install via `requirements.txt`, and exits with status 1.

3.  **`.env` file missing:**
    ```bash
    # Ensure .venv is active and requirements.txt installed
    # Temporarily rename/remove .env file from project root
    # mv .env .env.bak 
    python environment_setup/env_checker.py
    # mv .env.bak .env # Restore afterwards
    ```
    *Expected*: Script prints WARN message about missing `.env`, provides INSTRUCTION and template to create it, and exits (note: `env_checker.py` currently doesn't exit with status 1 if only the `.env` file is missing, but it does provide guidance).

### Unit Tests for `env_checker.py`

Unit tests for `env_checker.py` should be placed in `environment_setup/tests/unit/`. These tests would typically use `unittest.mock` to:
- Mock `importlib` or direct `import` statements to simulate missing dependencies.
- Mock `os.path.exists` to simulate the presence or absence of the `.env` file.
- Mock `sys.exit` to prevent tests from terminating and to assert it was called.
- Mock `builtins.print` (or capture `sys.stdout`/`sys.stderr`) to verify the script's output messages.

**Example (conceptual) test structure using `pytest` and `unittest.mock`:**

```python
# In environment_setup/tests/unit/test_env_checker.py

import pytest
from unittest import mock
import os
import sys

# Assuming env_checker.py is structured to be importable
from environment_setup import env_checker 

def test_ensure_dependencies_installed_all_ok(capsys):
    # Assuming dependencies are actually installed in test environment
    # or mock successful imports
    env_checker.ensure_dependencies_installed()
    captured = capsys.readouterr()
    assert "[INFO] cased/kit library found." in captured.out
    assert "[INFO] python-dotenv library found." in captured.out
    assert "[INFO] Core dependencies (kit, python-dotenv) are installed." in captured.out

@mock.patch('builtins.__import__', side_effect=ImportError("Simulated import error for kit"))
def test_ensure_dependencies_missing_kit(mock_import, capsys):
    with pytest.raises(SystemExit) as e:
        env_checker.ensure_dependencies_installed()
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "[ERROR] The 'cased/kit' library is not installed or not found." in captured.err
    assert "[INSTRUCTION] Please ensure you have set up the Python virtual environment" in captured.err

# ... more tests for check_and_setup_env_vars ...
```

**To run unit tests (from project root):**
```bash
pytest environment_setup/tests/unit/
```

## Test Structure

- `unit/`: Contains unit tests for `env_checker.py` (e.g., `test_env_checker.py`).
- `integration/`: (Currently N/A for this module, as its primary function is local environment checking rather than interacting with other live Codomyrmex modules in a complex way).
- `fixtures/` or `data/`: Could be used for sample `.env` content or directory structures if tests become more complex.

## Writing Tests

-   Follow the existing testing patterns using `pytest`.
-   Unit tests should focus on isolating functions in `env_checker.py`.
-   Mock external interactions like file system checks (`os.path.exists`) and imports (`builtins.__import__` or module-level mocks).
-   Verify calls to `sys.exit` and capture/assert printed output.

## Troubleshooting Failed Tests

-   **Unit Tests**:
    -   Check mock configurations: Ensure mocks behave as expected (e.g., `side_effect` for raising errors, correct `return_value`).
    -   Verify assertions against captured output: Ensure strings match exactly, including newlines or prefixes like `[ERROR]`.
    -   Ensure `env_checker.py`'s functions are being called as expected within the test.
-   **Manual Tests**:
    -   Ensure the pre-conditions for each manual test case (e.g., `.env` file deleted, package uninstalled) are correctly set up before running `env_checker.py`.
    -   Carefully observe the console output for the expected messages and exit behavior. 