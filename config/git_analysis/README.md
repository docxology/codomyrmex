# Git Analysis Configuration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git history analysis, contributor statistics, and commit pattern detection. Provides 16 analysis tools for repository insights including hotspot detection and code churn.

## Configuration Options

The git_analysis module operates with sensible defaults and does not require environment variable configuration. Analysis operates on the current git repository by default. Date ranges and file filters can be set per-analysis call.

## MCP Tools

This module exposes 3 MCP tool(s):

- `git_analysis_commit_history`
- `git_analysis_contributor_stats`
- `git_analysis_hotspots`

## PAI Integration

PAI agents invoke git_analysis tools through the MCP bridge. Analysis operates on the current git repository by default. Date ranges and file filters can be set per-analysis call.

## Validation

```bash
# Verify module is available
codomyrmex modules | grep git_analysis

# Run module health check
codomyrmex status
```

## Navigation

- [Source Module](../../src/codomyrmex/git_analysis/README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
