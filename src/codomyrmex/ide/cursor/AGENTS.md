# Codomyrmex Agents - src/codomyrmex/ide/cursor

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Cursor IDE integration module provides programmatic access to Cursor - the AI-first code editor. It enables automation of Cursor's AI-assisted development capabilities including Composer automation, rules management, and model configuration.

## Active Components

- `__init__.py` - CursorClient implementation for Cursor IDE automation
- `SPEC.md` - Technical specification for Cursor integration
- `README.md` - Module documentation

## Key Classes

- **CursorClient** - Client for interacting with Cursor IDE, extends `IDEClient`
  - `connect()` - Establish connection to Cursor workspace by detecting `.cursor` or `.cursorrules` files
  - `get_rules()` - Get current `.cursorrules` configuration content
  - `update_rules(rules)` - Update `.cursorrules` configuration
  - `get_models()` - List available AI models (GPT-4, Claude-3, etc.)
  - `set_model(model)` - Set the active AI model

## Operating Contracts

- Workspace detection is based on presence of `.cursor` directory or `.cursorrules` file
- Rules management operates on `.cursorrules` file in the workspace root
- Model selection validates against the known list of supported models
- All methods from `IDEClient` are implemented including `execute_command`, `get_active_file`, `open_file`, and `get_open_files`

## Signposting

- **Parent Directory**: [ide/](../README.md) - IDE integrations module
- **Sibling Modules**:
  - [vscode/](../vscode/README.md) - VSCode integration
  - [antigravity/](../antigravity/README.md) - Antigravity integration
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
