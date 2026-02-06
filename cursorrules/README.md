# cursorrules

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Hierarchical coding standards and automation rules for AI-assisted development across the Codomyrmex platform. Rules are organized by specificity level and applied in order of precedence.

## Rule Hierarchy

Rules follow a specificity hierarchy (most specific wins):

| Priority | Category | Location | Count |
|----------|----------|----------|-------|
| 1 (Highest) | File-specific | `file-specific/` | 6 rules |
| 2 | Module-specific | `modules/` | 60 rules |
| 3 | Cross-module | `cross-module/` | 8 rules |
| 4 (Lowest) | General | `general.cursorrules` | 1 rule |
| | **Total** | | **75 rules** |

## Directory Structure

```
cursorrules/
├── general.cursorrules       # Universal coding standards (baseline)
├── cross-module/             # Rules for cross-cutting concerns (8 rules)
│   ├── logging_monitoring.cursorrules
│   ├── model_context_protocol.cursorrules
│   ├── static_analysis.cursorrules
│   └── ... (5 more)
├── file-specific/            # Rules for specific file types (6 rules)
│   ├── python.cursorrules
│   ├── yaml.cursorrules
│   ├── json.cursorrules
│   └── ... (3 more)
└── modules/                  # Module-specific rules (60 rules)
    ├── security.cursorrules
    ├── agents.cursorrules
    ├── cloud.cursorrules
    └── ... (57 more)
```

## Standard Rule Template (8 Sections)

All `.cursorrules` files follow this structure:
0. **Preamble**: Relationship to general.cursorrules

1. **Purpose & Context**: Core functionality, key technologies
2. **Key Files & Structure**: Important files to monitor
3. **Coding Standards**: Language and style requirements
4. **Testing**: Test requirements and strategies
5. **Documentation**: Documentation maintenance
6. **Specific Considerations**: Module-specific notes
7. **Final Check**: Verification steps before finalizing

## Quick Reference

| Need | File |
|------|------|
| Python code standards | `file-specific/python.cursorrules` |
| Security guidelines | `modules/security.cursorrules` |
| Logging patterns | `cross-module/logging_monitoring.cursorrules` |
| MCP tool specs | `cross-module/model_context_protocol.cursorrules` |
| General principles | `general.cursorrules` |

## Companion Files

- [**AGENTS.md**](AGENTS.md) - AI agent guidelines for rule application
- [**SPEC.md**](SPEC.md) - Functional specification with architecture diagram
- [**PAI.md**](PAI.md) - Personal AI Infrastructure context

## Navigation

- **Project Root**: [../README.md](../README.md)
- **Source Code**: [../src/codomyrmex/](../src/codomyrmex/)
- **Documentation**: [../docs/](../docs/)
