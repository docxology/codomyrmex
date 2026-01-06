---
id: contributing
title: Contributing to Codomyrmex
sidebar_label: Contributing
---

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

1.  **Fork the repository**: `git clone https://github.com/YOUR_USERNAME/codomyrmex.git`
2.  **Set up your development environment**: Follow general setup instructions in the main `README.md` or specific instructions in a module's `README.md` if you are working within a particular module. Refer to the [Environment Setup Guide](../development/environment-setup.md) for detailed setup instructions.
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

## Code of Conduct

All contributors are expected to read and adhere to the project's [Code of Conduct](./code-of-conduct.md). Please ensure you are familiar with its contents.

## Questions?

If you have questions about contributing, project structure, or anything else, feel free to open an issue or use designated project communication channels. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
