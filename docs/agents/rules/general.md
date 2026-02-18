# General Cursor Rules

This document outlines the general coding standards and rules for the Codomyrmex project, migrated from the legacy `.cursorrules` configuration.

## Core Directives

1. **Maximum Intelligence & Relevance**: All code and responses must be of the highest quality, demonstrating deep understanding of the task.
2. **Modular & Functional**: Code should be modular, reusable, and follow functional programming principles where appropriate.
3. **No Mocks**: Always use real, functional methods. Testing should verify actual behavior, not mocked interactions.
4. **Verification**: Triple-check all filenames, paths, and signposting. Ensure documentation matches code.
5. **Pythonic Style**: Use standard Python conventions (PEP 8) and `uv` for environment management.
6. **Documentation**: All methods and modules must be documented. `AGENTS.md`, `README.md`, and `SPEC.md` must be maintained at all folder levels.
7. **Testing**: Maintain a modular, unified, and streamlined test suite.
8. **Step-by-Step**: Proceed comprehensively and intelligently.

## Specific Rules

* **Environment**: Use `uv` for all environment setup and package management.
* **Version Control**: structured git commits with clear messages.
* **Error Handling**: specific exceptions (like `NetworkingError`) over generic ones.

## Agent Behavior

* **Proactive**: Anticipate needs but confirm major decisions.
* **Concise**: Keep communication clear and to the point.
* **Safety**: Never run potentially destructive commands without confirmation.
