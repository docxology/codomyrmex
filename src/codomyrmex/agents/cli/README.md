# agents/cli

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

CLI agent implementation. Provides command handlers for interacting with multiple AI coding agents (Jules, Claude, Codex, OpenCode, Gemini, Droid) through a unified command-line interface. Each agent exposes execute, stream, and check operations.

## Key Exports

Imported from `handlers`:

- **`handle_info`** -- Display agent information
- **`handle_agent_setup`** -- Initialize and configure an agent
- **`handle_agent_test`** -- Run agent test/validation
- **`handle_jules_execute`** -- Execute a Jules agent command
- **`handle_jules_stream`** -- Stream output from Jules agent
- **`handle_jules_check`** -- Check Jules agent availability
- **`handle_jules_help`** -- Display Jules agent help
- **`handle_jules_command`** -- Send a raw command to Jules
- **`handle_claude_execute`** -- Execute a Claude agent command
- **`handle_claude_stream`** -- Stream output from Claude agent
- **`handle_claude_check`** -- Check Claude agent availability
- **`handle_codex_execute`** -- Execute a Codex agent command
- **`handle_codex_stream`** -- Stream output from Codex agent
- **`handle_codex_check`** -- Check Codex agent availability
- **`handle_opencode_execute`** -- Execute an OpenCode agent command
- **`handle_opencode_stream`** -- Stream output from OpenCode agent
- **`handle_opencode_check`** -- Check OpenCode agent availability
- **`handle_opencode_init`** -- Initialize OpenCode agent environment
- **`handle_opencode_version`** -- Display OpenCode agent version
- **`handle_gemini_execute`** -- Execute a Gemini agent command
- **`handle_gemini_stream`** -- Stream output from Gemini agent
- **`handle_gemini_check`** -- Check Gemini agent availability
- **`handle_gemini_chat_save`** -- Save a Gemini chat session
- **`handle_gemini_chat_resume`** -- Resume a saved Gemini chat
- **`handle_gemini_chat_list`** -- List saved Gemini chat sessions
- **`handle_droid_start`** -- Start the Droid agent
- **`handle_droid_stop`** -- Stop the Droid agent
- **`handle_droid_status`** -- Check Droid agent status
- **`handle_droid_config_show`** -- Display Droid configuration

## Directory Contents

- `__init__.py` - Package init; imports all handler functions from `handlers`
- `handlers.py` - CLI handler implementations for all supported agents
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [agents](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
