# Git Analysis -- Configuration Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the git_analysis module. Git history analysis, contributor statistics, and commit pattern detection.

## Configuration Requirements

Before using git_analysis in any PAI workflow, ensure:

1. The module is importable via `from codomyrmex.git_analysis import *`
2. Any optional dependencies are installed (check with `codomyrmex check`)

## Agent Instructions

1. Import the module directly: `from codomyrmex.git_analysis import ...`
2. Check module availability with `list_modules()` from system_discovery
3. Available MCP tools: `git_analysis_commit_history`, `git_analysis_contributor_stats`, `git_analysis_hotspots`
4. Analysis operates on the current git repository by default. Date ranges and file filters can be set per-analysis call.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("git_analysis.setting")

# Update configuration
set_config("git_analysis.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/git_analysis/AGENTS.md)
