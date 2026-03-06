# Git Operations -- Configuration Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the git_operations module. Version control automation with 35 git operation tools.

## Configuration Requirements

Before using git_operations in any PAI workflow, ensure:

1. `GITHUB_TOKEN` is set -- GitHub personal access token for API operations

## Agent Instructions

1. Verify required environment variables are set before invoking git_operations tools
2. Use `get_config("git_operations.<key>")` from config_management to read module settings
3. Available MCP tools: `git_commit`, `git_push`, `git_pull`, `git_branch`, `git_list_branches`
4. GitHub API operations require GITHUB_TOKEN. Git operations use the system git binary. GIT_EDITOR and GIT_TERMINAL_PROMPT are managed internally.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("git_operations.setting")

# Update configuration
set_config("git_operations.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/git_operations/AGENTS.md)
