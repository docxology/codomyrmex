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

The Codomyrmex project employs a hybrid approach to dependency management to balance clarity, modularity, and reproducibility:

1.  **Root `requirements.txt`**:
    *   This file, located at the project root, should list core dependencies essential for the overall project structure, development tooling (e.g., global linters, pre-commit hooks not specific to a module), or shared utilities used across multiple modules.
    *   Dependencies listed here should be broadly applicable.

2.  **Module-Specific `requirements.txt`**:
    *   Each individual module (e.g., `ai_code_editing/`, `data_visualization/`) should have its own `requirements.txt` file.
    *   This file lists dependencies required *only* for that specific module to function.
    *   This approach keeps modules self-contained and prevents unnecessary installation of dependencies for users or developers who are only interested in a subset of modules.

3.  **Version Pinning**:
    *   **All** `requirements.txt` files (both root and module-specific) **must** use version pinning for every listed dependency.
    *   Specify exact versions (e.g., `library_name==1.2.3`) rather than ranges or unpinned versions. This is crucial for ensuring reproducible builds and avoiding unexpected behavior due to automatic updates of transitive dependencies.
    *   When adding or updating a dependency, determine and specify the exact version that has been tested and confirmed to work.

4.  **Review and Justification**:
    *   When adding a new dependency, consider whether it should be in the root `requirements.txt` or a module-specific one.
    *   Be prepared to justify the inclusion of new dependencies in pull requests, especially for the root file.

This strategy aims to make the project manageable as it scales, allowing individual modules to evolve their dependencies without impacting others, while ensuring a stable and predictable environment for all contributors.

## Code of Conduct

All contributors are expected to follow professional and respectful communication standards. Please ensure your contributions align with the project's values and maintain a positive collaborative environment.

## Questions?

If you have questions about contributing, project structure, or anything else, feel free to open an issue or use designated project communication channels.

