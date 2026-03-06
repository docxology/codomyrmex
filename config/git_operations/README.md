# Git Operations Configuration

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Version control automation with 35 git operation tools. Provides branch management, commit operations, PR workflows, and repository management via GitHub API.

## Quick Configuration

```bash
export GITHUB_TOKEN=""    # GitHub personal access token for API operations (required)
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `GITHUB_TOKEN` | str | None | GitHub personal access token for API operations |

## MCP Tools

This module exposes 5 MCP tool(s):

- `git_commit`
- `git_push`
- `git_pull`
- `git_branch`
- `git_list_branches`

## PAI Integration

PAI agents invoke git_operations tools through the MCP bridge. GitHub API operations require GITHUB_TOKEN. Git operations use the system git binary. GIT_EDITOR and GIT_TERMINAL_PROMPT are managed internally.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep git_operations

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/git_operations/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
