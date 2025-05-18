# Git Operations Module

## Overview

The Git Operations module is designed to provide a standardized interface and a set of tools for performing common Git actions programmatically within the Codomyrmex ecosystem. This can be used by other modules, AI agents, or CI/CD processes to interact with Git repositories, manage branches, commits, and other version control tasks.

## Key Components

- **Git Command Wrapper**: A library or set of functions that wrap common `git` CLI commands (e.g., `clone`, `commit`, `push`, `pull`, `branch`, `checkout`, `status`). This aims to provide a more Pythonic or structured way to interact with Git than direct `subprocess` calls.
- **Repository State Analyzer**: Tools to parse `git status`, `git log`, and other commands to understand the current state of a repository (e.g., current branch, uncommitted changes, commit history).
- **MCP Tools for Git**: (If applicable) Exposing Git operations as tools callable via the Model Context Protocol, allowing LLMs to request Git actions. Example: `git.create_branch`, `git.commit_changes`.

## Integration Points

- **Provides**:
    - Functions/API for Git operations (see [API Specification](./API_SPECIFICATION.md)).
    - MCP tools for Git interactions (see [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md)).
- **Consumes**:
    - File system access to Git repositories.
    - Configuration for Git (e.g., user name, email, credentials - potentially managed by `environment_setup`).

## Getting Started

### Prerequisites

- `git` command-line tool must be installed and available in the system PATH.
- Potentially, SSH keys configured for accessing remote repositories if push/pull operations are involved.

### Installation

This module is part of Codomyrmex. Ensure it is included in your Python environment.

### Configuration

- **Git User**: Ensure `git config user.name` and `git config user.email` are set in the environment where this module operates, or provide these configurations to the module if it's performing commits.
- **Authentication**: For operations requiring remote interaction (push, pull, clone private repos), Git must be able to authenticate. This could be via SSH keys, Git credential manager, or tokens.

## Development

### Code Structure

(To be detailed based on implementation)
- `git_utils.py` (example): Core library for Git command wrapping.
- `mcp_tools.py` (example): Definitions for Git-related MCP tools.

### Building & Testing

- Tests would involve creating temporary Git repositories, performing operations, and asserting the state of the repository.
- Mocking `git` CLI calls might be necessary for some unit tests.

## Further Information

- [API Specification](./API_SPECIFICATION.md)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md)
- [Usage Examples](./USAGE_EXAMPLES.md)
- [Detailed Documentation](./docs/index.md)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md) 