# ide/antigravity

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Integration with Google DeepMind's Antigravity IDE -- the agentic AI coding assistant. Provides programmatic access to Antigravity's capabilities for meta-level control and automation including artifact management, conversation context, tool invocation, CLI/GUI chat integration, and session statistics.

## Key Exports

### Data Classes

- **`Artifact`** -- Represents an Antigravity conversation artifact with name, path, type (task/implementation_plan/walkthrough/other), optional content, size, and modification timestamp
- **`ConversationContext`** -- Represents the current conversation context with conversation ID, task name, task status, mode, and a list of associated artifacts

### Client

- **`AntigravityClient`** -- Main client extending `IDEClient` for Antigravity integration. Key features:

  **Connection and Session Management**
  - `connect()` -- Detect active Antigravity sessions by scanning `~/.gemini/antigravity/brain/` for conversation directories
  - `disconnect()` -- Clean up connection state
  - `is_connected()` -- Check connection status
  - `get_capabilities()` -- Return supported tools, artifact types, and features
  - `get_session_stats()` -- Retrieve connection status, artifact count, command history, and success rate
  - `list_conversations()` -- List recent conversations with metadata
  - `switch_conversation()` -- Switch to a different conversation by ID

  **Tool Integration** (18 built-in tools)
  - `execute_command()` -- Execute an Antigravity tool command
  - `invoke_tool()` -- Higher-level tool invocation with IDECommandResult
  - `get_tool_info()` -- Get parameter details for tools including: `task_boundary`, `notify_user`, `write_to_file`, `replace_file_content`, `multi_replace_file_content`, `view_file`, `view_file_outline`, `view_code_item`, `run_command`, `command_status`, `send_command_input`, `find_by_name`, `grep_search`, `list_dir`, `browser_subagent`, `generate_image`, `search_web`, `read_url_content`

  **Chat and Communication**
  - `send_chat_message()` -- Send messages via CLI (`antigravity`/`agy`) with mode support, falling back to simulated notify_user
  - `send_chat_gui()` -- GUI automation via AppleScript for macOS; sends keystrokes directly to the Antigravity application window

  **Artifact Management**
  - `list_artifacts()` -- List all artifacts in the current conversation
  - `get_artifact()` -- Read artifact content by name
  - `create_artifact()` -- Create new Markdown artifacts (task, implementation_plan, walkthrough, other)
  - `update_artifact()` -- Update existing artifact content
  - `delete_artifact()` -- Remove an artifact

  **File Operations**
  - `get_active_file()` / `open_file()` / `get_open_files()` -- IDE file management

  **Agent Relay & Live Bridge**
  - `AgentRelay` -- File-based JSONL message bus for process-independent inter-agent communication
  - `LiveAgentBridge` -- connects Antigravity to the relay with background polling and auto-tool execution
  - `ClaudeCodeEndpoint` -- connects Claude Code to the relay with auto-respond capabilities
  - `relay_cli` -- Command-line interface for managing channels and sending messages

## Directory Contents

- `__init__.py` - AntigravityClient, Artifact, ConversationContext, and tool info registry (798 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [ide](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
