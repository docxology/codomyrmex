# Codomyrmex Agents — src/codomyrmex/agents/git_agent

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Git Agent module providing automated git operations and version control management. This module enables AI-assisted git workflows including commit message generation, branch management, and repository analysis.

## Active Components

- `agent.py` - Main GitAgent implementation
- `__init__.py` - Module exports
- `README.md` - Module documentation

## Key Classes

### Agent
- **`GitAgent`** - Primary agent for git operations
  - Executes git commands programmatically
  - Generates commit messages based on changes
  - Manages branch operations (create, switch, merge)
  - Analyzes repository state and history
  - Handles staging, committing, and pushing
  - Supports conflict detection and resolution hints

## Operating Contracts

- Requires git to be installed and accessible in PATH.
- Operations are performed in the current working directory by default.
- Follows safe git practices (no force pushes without explicit request).
- Validates repository state before operations.
- Provides descriptive error messages for git failures.

## Signposting

- **Committing changes?** Use `GitAgent` for AI-assisted commit messages.
- **Branch management?** Use `GitAgent` methods for branch operations.
- **Repository analysis?** Query `GitAgent` for status, history, and diffs.
- **Integration?** `GitAgent` can be used standalone or with other agents.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Core Module**: [core](../core/AGENTS.md) - Base classes and interfaces
- **Project Root**: ../../../../README.md - Main project documentation
