# Personal AI Infrastructure - Cursor Rules Context

**Directory**: `cursorrules/`
**Status**: Active | **Last Updated**: February 2026

## Overview

The `cursorrules/` directory contains **75 rules** for AI-assisted development, organized hierarchically by specificity. Rules encode mandatory project policies (Zero-Mock, UV, RASP, Python ≥ 3.10) alongside coding standards and best practices.

## Statistics

| Category | Count |
|----------|-------|
| Module-specific rules | 60 |
| Cross-module rules | 8 |
| File-specific rules | 6 |
| General rules | 1 |
| **Total** | **75** |

## Mandatory Policies

These policies are encoded in `general.cursorrules §2` and enforced globally:

| Policy | Key Implication |
|--------|----------------|
| **Zero-Mock** | All `.cursorrules` testing sections use real implementations |
| **UV-Only** | All Key Files sections reference `pyproject.toml`, not `requirements.txt` |
| **RASP** | All subdirectories contain README.md, AGENTS.md, SPEC.md, PAI.md |
| **Python ≥ 3.10** | Type hints, match statements, and modern syntax expected |

## AI Context

When working with cursor rules:

1. **Rule Hierarchy**: Apply rules in order of specificity:
   - File-specific rules (highest priority)
   - Module-specific rules
   - Cross-module rules
   - General rules (lowest priority)

2. **Mandatory policies cannot be overridden** by any rule level — they apply universally.

3. **Module-Specific Rules**: Check `modules/{module_name}.cursorrules` first when editing a module.

4. **File-Specific Rules**: Check `file-specific/` for Python, YAML, JSON, and documentation files.

5. **Non-Executable**: Contains `.cursorrules` files, not Python code.

## Key Files

- `general.cursorrules`: Default coding standards + mandatory policies for the repository
- `modules/`: 60 module-specific rule files
- `cross-module/`: 8 cross-cutting concern rules
- `file-specific/`: 6 file-type specific rules

## Navigation

- **Parent**: [../README.md](../README.md)
- **Related Spec**: [SPEC.md](SPEC.md)
- **Agent Guidelines**: [AGENTS.md](AGENTS.md)
- **Modules Directory**: [modules/](modules/)
