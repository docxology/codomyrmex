# Git Operations Module

## Overview

The Git Operations module is designed to provide a standardized interface and a set of tools for performing common Git actions programmatically within the Codomyrmex ecosystem. This can be utilized by other modules, AI agents (if MCP tools are developed), or CI/CD processes to interact with Git repositories, manage branches, commits, and other version control tasks effectively and consistently.

**Note on Scope**: This module provides *tools* for Git automation. For guidelines on project-wide Git practices, such as branching strategy, commit message conventions, and the Pull Request (PR) process, please refer to the main [Codomyrmex Contributing Guidelines](../../CONTRIBUTING.md).

## Git Workflow Documentation

### Branching Strategy

The Codomyrmex project follows a feature branch workflow:

1. **Main Branch**: The `main` branch represents the primary line of development, always aiming to be stable and production-ready.
2. **Feature Branches**: Development occurs on separate branches with descriptive names:
   - `feature/description` - New features
   - `fix/description` - Bug fixes
   - `docs/description` - Documentation updates
   - `refactor/description` - Code refactoring
   - `test/description` - Test additions/changes
3. **Release Branches**: For release preparation: `release/v1.x.x`
4. **Hotfix Branches**: For critical production fixes: `hotfix/description`

### Commit Conventions

The project follows [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

**Example**:
```
feat(git_operations): Add branch validation in create_branch

Add validation to ensure branch names follow naming conventions
before creating new branches.

Closes #123
```

### Pull Request Workflow

1. **Create Feature Branch**: Create and switch to a feature branch from `main`
   ```python
   from codomyrmex.git_operations import create_branch, switch_branch

   create_branch("feature/new-feature")
   ```

2. **Make Changes**: Implement changes and commit incrementally
   ```python
   from codomyrmex.git_operations import add_files, commit_changes

   add_files(["new_file.py", "modified_file.py"])
   commit_changes("feat: Add new feature implementation")
   ```

3. **Push Branch**: Push feature branch to remote
   ```python
   from codomyrmex.git_operations import push_changes

   push_changes(remote="origin", branch="feature/new-feature")
   ```

4. **Create Pull Request**: Use GitHub API to create PR
   ```python
   from codomyrmex.git_operations import create_pull_request

   create_pull_request(
       repo="user/repo",
       title="feat: Add new feature",
       body="Description of changes",
       head="feature/new-feature",
       base="main"
   )
   ```

5. **Review and Merge**: After review and CI checks pass, merge PR (typically via GitHub UI or API)

### Typical Workflow Example

```python
from codomyrmex.git_operations import (
    check_git_availability,
    is_git_repository,
    create_branch,
    add_files,
    commit_changes,
    push_changes,
    get_current_branch
)

# Verify Git is available
if not check_git_availability():
    print("Git is not available")
    exit(1)

# Ensure we're in a Git repository
if not is_git_repository():
    print("Not a Git repository")
    exit(1)

# Create feature branch
feature_branch = "feature/new-authentication"
if create_branch(feature_branch):
    print(f"Created and switched to {feature_branch}")

    # Make changes (create/modify files)
    # ... code changes ...

    # Stage and commit
    add_files(["auth.py", "test_auth.py"])
    commit_changes("feat(auth): Add new authentication system")

    # Push to remote
    if push_changes(branch=feature_branch):
        print(f"Pushed {feature_branch} to remote")
        print(f"Create PR from {feature_branch} to main")
```

This module provides tools to automate all parts of this workflow, including:
- Creating feature branches with conventional names
- Validating commit messages (can be integrated)
- Automating PR creation
- Extracting information for release notes from Git history

## Key Components

- **Git Command Wrapper/Library**: A core set of Python functions that abstract and wrap common `git` command-line interface (CLI) commands (e.g., `clone`, `commit`, `push`, `pull`, `branch`, `checkout`, `status`, `log`, `diff`). This aims to provide a robust, error-handled, and Pythonic way to interact with Git repositories, often using libraries like `GitPython` or by managing `subprocess` calls carefully.
- **Repository State Analyzer**: Utility functions to parse the output of Git commands (like `git status --porcelain`, `git log --pretty=format:%H;%an;%ae;%s`) to provide structured information about the current state of a repository. This includes details such as the current branch, uncommitted changes, commit history, and differences between commits or branches.
- **Configuration Management**: Mechanisms to handle Git configurations essential for operations, such as user name, email, and authentication credentials. This component would integrate with the `environment_setup` module for sourcing credentials securely (e.g., from environment variables or a Git credential helper).
- **Error Handling and Logging**: Consistent error reporting for failed Git operations and integration with the `logging_monitoring` module for detailed logging of actions performed.

## Integration Points

This module interacts with the system and other Codomyrmex modules as follows:

- **Provides:**
    - A Python API for performing Git operations (e.g., functions in `git_utils.py` or similar). See the [API Specification](./API_SPECIFICATION.md) (currently a template, to be detailed as the module is implemented).
    - Potentially, MCP tools for Git interactions if specific use cases for AI-driven Git operations arise (see [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) - currently N/A).
    - Structured data about repository state, commit history, and diffs.

- **Consumes:**
    - **File System Access**: Requires access to local Git repositories on the file system to execute commands.
    - **`git` CLI Tool**: Relies on the `git` command-line tool being installed and accessible in the system PATH.
    - **Git Configuration**: Uses system-level Git configuration (e.g., `~/.gitconfig`) and repository-level configuration (`.git/config`) for user identity (name, email) and remote repository details.
    - **Authentication Credentials**: For operations involving remote repositories (clone, fetch, pull, push), it requires appropriate authentication mechanisms to be in place (e.g., SSH keys, HTTPS tokens via a credential manager). The `environment_setup` module may play a role in guiding the setup of these credentials.
    - **`logging_monitoring` module**: For logging all Git operations performed, their outcomes, and any errors encountered.
    - **`environment_setup` module**: To verify the presence of `git` and potentially to assist in configuring credentials.

## Getting Started

Using this module typically involves importing its functions into other Python scripts or modules within the Codomyrmex project.

### Prerequisites

- **`git` Command-Line Tool**: Must be installed on the system and accessible in the PATH environment variable.
- **Python Environment**: A Python environment (as set up by the `environment_setup` module) with necessary dependencies for this module (e.g., `GitPython` if used, see `git_operations/requirements.txt`).
- **Repository Access**: The user or process executing scripts that use this module must have appropriate read/write permissions for the target Git repositories.

### Installation

This module is an integral part of the Codomyrmex project. Its availability is ensured by cloning the Codomyrmex repository and setting up the Python environment as described in the main project `README.md` or `environment_setup/README.md`.

If this module has specific Python dependencies not covered by the root configuration, they should be listed in `git_operations/requirements.txt` and installed:
```bash
uv pip install -r src/codomyrmex/git_operations/requirements.txt
```

### Configuration

- **Git User Identity**: For operations that create commits (e.g., `git commit`), ensure that `git config user.name` and `git config user.email` are set appropriately in the global, system, or repository Git configuration. The module functions might also accept these as parameters.
- **Authentication for Remotes**: For interactions with remote repositories (e.g., `push`, `pull`, `clone` of private repositories), Git must be configured to authenticate correctly. This typically involves:
    - SSH keys (with `ssh-agent`)
    - HTTPS with a credential manager or personal access tokens (PATs).
    - Refer to Git documentation and `environment_setup` guidance for secure credential management.

## Development

Developers contributing to this module should focus on creating robust, secure, and well-tested Git interaction utilities.

### Code Structure

The `git_operations` module is expected to be organized as follows:

- `README.md`: This file.
- `__init__.py`: Makes the directory a Python package and may expose key functions.
- `git_wrapper.py` (or `git_utils.py`): Contains the core Python functions that wrap `git` CLI commands or use a library like `GitPython`.
- `repository.py` (example): Could contain classes or functions for representing and analyzing Git repository state.
- `exceptions.py` (example): Custom exceptions for Git-related errors.
- `API_SPECIFICATION.md`: (To be detailed) Describes the public API of this module (functions, classes).
- `MCP_TOOL_SPECIFICATION.md`: (Currently N/A) Would define any MCP tools if developed.
- `requirements.txt`: Module-specific Python dependencies (e.g., `GitPython`).
- `docs/`: Detailed documentation:
    - `technical_overview.md`: Architectural details.
    - `tutorials/`: How-to guides for using the module's API.
- `tests/`: Unit and integration tests:
    - `unit/`: Tests for individual functions, potentially mocking `subprocess` or Git library calls.
    - `integration/`: Tests that interact with actual (temporary or local) Git repositories.

### Building & Testing

- **Building**: As a Python module, no separate compilation or build step is typically required beyond ensuring dependencies are installed.
- **Testing**:
    1.  **Install Dependencies**: Ensure all project and module-specific development dependencies are installed (including testing frameworks like `pytest`).
        ```bash
        uv pip install -e .
        uv pip install -r src/codomyrmex/git_operations/requirements.txt
        uv pip install pytest pytest-mock
        ```
    2.  **Run Tests**: Execute tests using a test runner like `pytest`. Tests should cover various Git commands and repository states.
        ```bash
        # From the project root directory
        pytest git_operations/tests/
        ```
    - **Unit Tests (`tests/unit`)**: Focus on testing the logic of wrapper functions, argument parsing, and output processing. External `git` calls should be mocked (e.g., using `unittest.mock` or `pytest-mock`) to ensure tests are fast and deterministic.
    - **Integration Tests (`tests/integration`)**: Involve creating temporary local Git repositories, performing a sequence of operations using the module's functions, and then asserting the state of the repository (e.g., branches, commits, file status) by querying it with `git` CLI commands or the module's own state analysis functions.

Ensure all contributions pass tests and adhere to project coding standards.

## Further Information

- [API Specification](./API_SPECIFICATION.md)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](./USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md)
