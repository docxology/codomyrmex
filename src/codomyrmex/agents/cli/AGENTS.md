# Codomyrmex Agents — src/codomyrmex/agents/cli

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

CLI module providing command-line interface handlers for all agent operations. This module centralizes CLI command handling for agent setup, testing, and execution across all supported agent backends.

## Active Components

- `handlers.py` - CLI command handler implementations
- `__init__.py` - Module exports
- `README.md` - Module documentation

## Key Functions

### General Handlers
- **`handle_info()`** - Display agent system information
- **`handle_agent_setup()`** - Setup and configure agents
- **`handle_agent_test()`** - Test agent connectivity and functionality

### Jules Handlers
- **`handle_jules_execute()`** - Execute Jules commands
- **`handle_jules_stream()`** - Stream Jules output
- **`handle_jules_check()`** - Check Jules availability
- **`handle_jules_help()`** - Display Jules help
- **`handle_jules_command()`** - Generic Jules command handler

### Claude Handlers
- **`handle_claude_execute()`** - Execute Claude requests
- **`handle_claude_stream()`** - Stream Claude responses
- **`handle_claude_check()`** - Check Claude API availability

### Codex Handlers
- **`handle_codex_execute()`** - Execute Codex requests
- **`handle_codex_stream()`** - Stream Codex responses
- **`handle_codex_check()`** - Check Codex API availability

### OpenCode Handlers
- **`handle_opencode_execute()`** - Execute OpenCode commands
- **`handle_opencode_stream()`** - Stream OpenCode output
- **`handle_opencode_check()`** - Check OpenCode availability
- **`handle_opencode_init()`** - Initialize OpenCode in project
- **`handle_opencode_version()`** - Display OpenCode version

### Gemini Handlers
- **`handle_gemini_execute()`** - Execute Gemini requests
- **`handle_gemini_stream()`** - Stream Gemini responses
- **`handle_gemini_check()`** - Check Gemini availability
- **`handle_gemini_chat_save()`** - Save Gemini chat session
- **`handle_gemini_chat_resume()`** - Resume Gemini chat session
- **`handle_gemini_chat_list()`** - List Gemini chat sessions

### Droid Handlers
- **`handle_droid_start()`** - Start droid controller
- **`handle_droid_stop()`** - Stop droid controller
- **`handle_droid_status()`** - Display droid status
- **`handle_droid_config_show()`** - Show droid configuration

## Operating Contracts

- Handlers follow consistent argument patterns.
- Output is formatted for terminal display.
- Errors are reported with actionable messages.
- Streaming handlers support real-time output.
- All handlers return appropriate exit codes.

## Signposting

- **Running agent commands?** Use the appropriate `handle_*_execute()` function.
- **Streaming output?** Use the appropriate `handle_*_stream()` function.
- **Checking availability?** Use the appropriate `handle_*_check()` function.
- **Droid operations?** Use `handle_droid_*` functions for task automation.
- **Integration?** Handlers can be called programmatically or from CLI.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Claude Agent**: [claude](../claude/AGENTS.md) - Claude integration
- **Codex Agent**: [codex](../codex/AGENTS.md) - Codex integration
- **Gemini Agent**: [gemini](../gemini/AGENTS.md) - Gemini integration
- **Jules Agent**: [jules](../jules/AGENTS.md) - Jules integration
- **OpenCode Agent**: [opencode](../opencode/AGENTS.md) - OpenCode integration
- **Droid Module**: [droid](../droid/AGENTS.md) - Task automation
- **Project Root**: ../../../../README.md - Main project documentation
