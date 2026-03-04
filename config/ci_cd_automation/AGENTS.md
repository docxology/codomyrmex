# CI CD Automation -- Configuration Agent Coordination

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for configuring and using the ci_cd_automation module. Continuous integration and deployment pipeline management.

## Configuration Requirements

Before using ci_cd_automation in any PAI workflow, ensure:

1. `CI_CD_API_TOKEN` is set -- Authentication token for CI/CD service API
2. `CI_CD_BASE_URL` is set -- Base URL of the CI/CD service endpoint

## Agent Instructions

1. Verify required environment variables are set before invoking ci_cd_automation tools
2. Use `get_config("ci_cd_automation.<key>")` from config_management to read module settings
3. Available MCP tools: `ci_run_pipeline`, `ci_get_status`, `ci_list_pipelines`
4. Pipeline definitions are typically stored as YAML. The module connects to external CI services via API token authentication.

## Operating Contracts

- **Import Safety**: Module import does not trigger side effects or network calls
- **Error Handling**: All errors raise specific exceptions (never returns None silently)
- **Thread Safety**: Configuration reads are thread-safe after initialization

## Configuration Patterns

```python
from codomyrmex.config_management.mcp_tools import get_config, set_config

# Read current configuration
value = get_config("ci_cd_automation.setting")

# Update configuration
set_config("ci_cd_automation.setting", "new_value")
```

## PAI Agent Role Access Matrix

| PAI Agent | Config Access | Notes |
|-----------|--------------|-------|
| Engineer | Read/Write | Can update configuration during setup |
| Architect | Read | Reviews configuration for compliance |
| QATester | Read | Validates configuration before test runs |
| Researcher | Read | No configuration changes |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source Module](../../src/codomyrmex/ci_cd_automation/AGENTS.md)
