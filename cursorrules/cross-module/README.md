# cross-module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Cross-module cursor rules for multi-module interactions and shared patterns. These rules apply when working across module boundaries or with cross-cutting concerns.

## Rule List (8 rules)

| Rule | Purpose |
|------|---------|
| `build_synthesis.cursorrules` | Build processes and code synthesis operations |
| `data_visualization.cursorrules` | Plotting, charting, and visualization patterns |
| `logging_monitoring.cursorrules` | Structured logging, metrics, and observability |
| `model_context_protocol.cursorrules` | MCP tool and resource specifications |
| `output_module.cursorrules` | Output directory management and artifact handling |
| `pattern_matching.cursorrules` | Code analysis and pattern matching operations |
| `static_analysis.cursorrules` | Linting, security scanning, code quality |
| `template_module.cursorrules` | Template usage and customization patterns |

## Usage

Cross-module rules apply to:

- Operations involving multiple modules
- Shared infrastructure (logging, metrics, output)
- Cross-cutting concerns (static analysis, MCP)
- Template-based code generation

## Rule Hierarchy Position

```
file-specific/ (highest priority)
    ↓
modules/
    ↓
cross-module/ ← You are here
    ↓
general.cursorrules (lowest priority)
```

## Companion Files

- [**AGENTS.md**](AGENTS.md) - Agent guidelines for cross-module work
- [**SPEC.md**](SPEC.md) - Functional specification

## Navigation

- **Parent Directory**: [../README.md](../README.md)
- **File-Specific Rules**: [../file-specific/](../file-specific/)
- **Module Rules**: [../modules/](../modules/)
- **Project Root**: [../../README.md](../../README.md)
