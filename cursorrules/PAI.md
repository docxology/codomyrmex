# Personal AI Infrastructure - Cursor Rules Context

**Directory**: `cursorrules/`
**Status**: Active

## Overview

The `cursorrules/` directory contains coding standards, linting rules, and automation patterns specifically designed for AI-assisted development tools like Cursor IDE.

## AI Context

When working with cursor rules:

1. **Apply Rules Consistently**: Agents should read and apply the rules in `general.cursorrules` when generating code.
2. **Module-Specific Rules**: Some modules have their own cursorrules in `modules/`. Check for these first.
3. **Non-Executable**: This directory contains `.cursorrules` files (YAML/text), not Python code.

## Key Files

- `general.cursorrules`: Default coding standards for the repository
- `modules/`: Module-specific overrides

## Navigation

- **Parent**: [../README.md](../README.md)
- **Related Spec**: [SPEC.md](SPEC.md)
