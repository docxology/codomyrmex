# Contributing to Codomyrmex

Thank you for your interest in contributing to the Codomyrmex project! We appreciate the community's efforts to help us improve and grow this modular, extensible coding workspace.

This document provides guidelines for contributing to the overall Codomyrmex project. For contributions to specific modules, please also refer to the `CONTRIBUTING.md` file within that module's directory, which may contain more specific instructions for its language, tools, or development setup.

## How to Contribute

We welcome contributions in various forms, including but not limited to:

- **Reporting Bugs and Issues**: If you find a bug in the core framework or any module, please open an issue in the main project repository.
- **Suggesting New Features or Enhancements**: Ideas for new modules, core features, or improvements to existing ones are welcome. Please open an issue to discuss.
- **Writing or Improving Documentation**: Clear documentation is crucial. This includes the main project README, module READMEs, API specifications, tutorials, and other documents.
- **Submitting Pull Requests**: For code changes (bug fixes, new features, improvements) to the core project or individual modules.
- **Participating in Discussions**: Share your feedback, ideas, and use cases.

## Getting Started

1.  **Fork the repository**: `git clone https://github.com/codomyrmex/codomyrmex.git`
2.  **Set up your development environment**: Follow general setup instructions in the main `README.md` or specific instructions in a module's `README.md` if you are working within a particular module.
3.  **Create a new branch** for your work: `git checkout -b type/descriptive-branch-name` (e.g., `feature/new-visualization-tool`, `bugfix/readme-typo`, `docs/improve-contributing-guide`).

## Reporting Bugs

- **Search existing issues** to avoid duplicates.
- If not found, **open a new issue**.
- Provide a **clear and descriptive title**.
- Include **detailed steps to reproduce the bug**:
    - Project/module version(s) affected.
    - Your operating system and version.
    - Relevant configuration details.
    - Expected behavior vs. actual behavior.
    - Screenshots, logs, or error messages if applicable.

## Suggesting Enhancements

- **Open a new issue** to discuss your idea.
- Clearly explain the **problem you're solving** or the **improvement you envision**.
- Detail your **proposed solution** and its **benefits** to the project.

## Pull Request Guidelines

- **Scope**: Each PR should address a single, focused issue or feature. Break down larger changes into smaller, manageable PRs.
- **Code Style**: Adhere to the coding style and conventions used in the project or specific module. Run linters/formatters as specified.
- **Documentation**: Update or add documentation relevant to your changes (e.g., READMEs, API specs, code comments, usage examples).
- **Tests**:
    - Add new tests for any new functionality.
    - Ensure all existing and new tests pass before submitting.
    - Refer to the module's `tests/README.md` for testing instructions.
- **Commit Messages**: Write clear, concise, and descriptive commit messages. Consider using [Conventional Commits](https://www.conventionalcommits.org/) if the project adopts this standard.
- **Rebase**: Keep your branch updated with the latest changes from the main development branch by rebasing your changes.
- **PR Description**: Provide a clear description of the changes in your pull request, linking to any relevant issues (e.g., `Fixes #123`).

### PR Process

1.  Ensure your code builds and all tests pass locally.
2.  Submit your pull request to the appropriate branch in the main Codomyrmex repository.
3.  The maintainers will review your PR. Be prepared for discussions and make adjustments based on feedback.
4.  Once approved and all checks pass, your PR will be merged.

## Dependency Management

The Codomyrmex project uses **pyproject.toml as the single source of truth** for all dependency management to ensure reproducibility, security, and maintainability.

### Current Strategy (Effective January 2026)

1.  **Single Source of Truth: `pyproject.toml`**:
    *   All dependencies are defined in `pyproject.toml` with version constraints.
    *   Core dependencies are listed in `[project.dependencies]` and are installed by default.
    *   Module-specific optional dependencies are listed in `[project.optional-dependencies]` and can be installed per module.

2.  **Version Pinning**:
    *   All production dependencies **must** use minimum version constraints (e.g., `package>=1.2.3`).
    *   The `uv.lock` file pins exact versions for reproducible builds.
    *   When adding or updating a dependency, specify a minimum version that has been tested and confirmed to work.

3.  **Installing Dependencies**:
    *   **Core dependencies**: `uv sync` (installs all core dependencies)
    *   **Module-specific dependencies**: `uv sync --extra <module-name>` (e.g., `uv sync --extra spatial`)
    *   **All optional dependencies**: `uv sync --all-extras`
    *   **Development dependencies**: Automatically included with `uv sync --dev`

4.  **Module-Specific `requirements.txt` Files**:
    *   **DEPRECATED**: Module-specific `requirements.txt` files are deprecated and will be removed in a future version.
    *   These files are kept temporarily for backward compatibility but should **not be modified**.
    *   All new dependencies must be added to `pyproject.toml` instead.

5.  **Adding New Dependencies**:
    *   **Core dependencies** (used by multiple modules): Add to `[project.dependencies]` in `pyproject.toml`
    *   **Module-specific dependencies**: Add to `[project.optional-dependencies.<module-name>]` in `pyproject.toml`
    *   **Development dependencies**: Add to `[tool.uv.dev-dependencies]` in `pyproject.toml`
    *   After adding, run `uv lock` to update the lock file
    *   Be prepared to justify the inclusion of new dependencies in pull requests

6.  **Dependency Validation**:
    *   Pre-commit hooks validate dependency consistency
    *   CI/CD checks for duplicate or conflicting dependencies
    *   See `tools/dependency_consolidator.py` for dependency analysis tools

This strategy ensures reproducible builds, reduces security risks from unpinned dependencies, and simplifies maintenance by having a single source of truth for all dependency information.

## Code of Conduct

All contributors are expected to follow professional and respectful communication standards. Please ensure your contributions align with the project's values and maintain a positive collaborative environment.

## Questions?

If you have questions about contributing, project structure, or anything else, feel free to open an issue or use designated project communication channels.


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../../README.md)
