# ide/cursor

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Integration with Cursor IDE -- the AI-first code editor. Provides programmatic access to Cursor's AI-assisted development capabilities including Composer automation, `.cursorrules` management, and model configuration.

## Key Exports

- **`CursorClient`** -- Client extending `IDEClient` for Cursor IDE integration. Key capabilities:

  **Connection**
  - `connect()` -- Detect a Cursor workspace by checking for `.cursor` directory or `.cursorrules` file
  - `disconnect()` -- Clean up connection state
  - `is_connected()` -- Check connection status
  - `get_capabilities()` -- Return supported features (composer, chat, inline_edit, code_generation, code_explanation, rules_management, model_selection) and available models

  **Rules Management**
  - `get_rules()` -- Read current `.cursorrules` configuration from the workspace root
  - `update_rules()` -- Write updated rules; accepts string or dict content (dicts are JSON-serialized)

  **Model Configuration**
  - `get_models()` -- List available AI models (gpt-4, gpt-4-turbo, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet)
  - `set_model()` -- Validate and set the active AI model

  **File Operations**
  - `execute_command()` -- Execute a Cursor command
  - `get_active_file()` / `open_file()` / `get_open_files()` -- IDE file management

## Directory Contents

- `__init__.py` - CursorClient with rules/model management and workspace detection (130 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [ide](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
