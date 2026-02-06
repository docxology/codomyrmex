# Personal AI Infrastructure - Cursor Rules Context

**Directory**: `cursorrules/`
**Status**: Active | **Last Updated**: February 2026

## Overview

The `cursorrules/` directory contains **75 rules** for AI-assisted development, organized hierarchically by specificity.

## Statistics

| Category | Count |
|----------|-------|
| Module-specific rules | 60 |
| Cross-module rules | 8 |
| File-specific rules | 6 |
| General rules | 1 |
| **Total** | **75** |

## AI Context

When working with cursor rules:

1. **Rule Hierarchy**: Apply rules in order of specificity:
   - File-specific rules (highest priority)
   - Module-specific rules
   - Cross-module rules
   - General rules (lowest priority)

2. **Module-Specific Rules**: Check `modules/{module_name}.cursorrules` first when editing a module.

3. **File-Specific Rules**: Check `file-specific/` for Python, YAML, JSON, and documentation files.

4. **Non-Executable**: Contains `.cursorrules` files, not Python code.

## Key Files

- `general.cursorrules`: Default coding standards for the repository
- `modules/`: 60 module-specific rule files
- `cross-module/`: 8 cross-cutting concern rules
- `file-specific/`: 6 file-type specific rules

## Navigation

- **Parent**: [../README.md](../README.md)
- **Related Spec**: [SPEC.md](SPEC.md)
- **Modules Directory**: [modules/](modules/)
