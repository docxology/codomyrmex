# Maintenance

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Tools Module for Codomyrmex.

## Architecture Overview

```
maintenance/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`deps`**
- **`health`**
- **`analyze_project_structure`**
- **`analyze_project_dependencies`**
- **`analyze_code_quality`**
- **`check_dependencies`**
- **`consolidate_dependencies`**
- **`add_deprecation_notice`**
- **`DependencyAnalyzer`**
- **`analyze_project_main`**
- **`dependency_analyzer_main`**
- **`dependency_checker_main`**
- **`dependency_consolidator_main`**
- **`validate_dependencies_main`**
- **`add_deprecation_notices_main`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `maintenance_health_check` | Safe |
| `maintenance_list_tasks` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/maintenance/](../../../../src/codomyrmex/maintenance/)
- **Parent**: [All Modules](../README.md)
