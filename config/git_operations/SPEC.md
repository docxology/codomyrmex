# Git Operations Configuration Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Version control automation with 35 git operation tools. Provides branch management, commit operations, PR workflows, and repository management via GitHub API. This specification documents the configuration schema and constraints.

## Configuration Schema

| Key | Type | Required | Default | Description |
|-----|------|----------|---------|-------------|
| `GITHUB_TOKEN` | string | Yes | None | GitHub personal access token for API operations |

## Environment Variables

```bash
# Required
export GITHUB_TOKEN=""    # GitHub personal access token for API operations
```

## Design Principles

- **Centralized Config**: All settings accessible via config_management module
- **Env-First**: Environment variables take precedence over config file values
- **Explicit Defaults**: All optional settings have documented defaults
- **Zero-Mock**: No placeholder or fake configuration values in production

## Constraints

- `GITHUB_TOKEN` must be set before module initialization
- Configuration is validated on first use; invalid values raise explicit errors
- No silent fallback to placeholder values

## Dependencies

**Depends on**: `config_management`, `environment_setup`

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source Module](../../src/codomyrmex/git_operations/SPEC.md)
