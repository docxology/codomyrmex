# Codomyrmex Agents - src/codomyrmex/ide/antigravity

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Antigravity IDE integration module provides programmatic access to Google DeepMind's Antigravity IDE - the agentic AI coding assistant. It enables meta-level control and automation including artifact management, tool invocation, conversation context access, and GUI automation via AppleScript.

## Active Components

- `__init__.py` - AntigravityClient implementation with full artifact and tool support
- `SPEC.md` - Technical specification for Antigravity integration
- `README.md` - Module documentation

## Key Classes

- **AntigravityClient** - Client for interacting with Antigravity IDE, extends `IDEClient`
  - `connect()` - Establish connection by scanning `~/.gemini/antigravity/brain/` for conversations
  - `list_artifacts()` - List conversation artifacts (tasks, implementation plans, walkthroughs)
  - `get_artifact(name)` - Retrieve specific artifact content
  - `create_artifact(name, content, type)` - Create new artifact with type validation
  - `update_artifact(name, content)` - Update existing artifact
  - `delete_artifact(name)` - Remove an artifact
  - `list_conversations(limit)` - List recent conversations with metadata
  - `switch_conversation(id)` - Switch to a different conversation
  - `invoke_tool(tool_name, parameters)` - Invoke Antigravity tools (view_file, run_command, etc.)
  - `send_chat_message(message)` - Send message via CLI (`antigravity` or `agy`) with fallback
  - `send_chat_gui(message, app_name)` - Send message via GUI automation (AppleScript)
  - `get_tool_info(tool_name)` - Get documentation for a specific tool
  - `get_session_stats()` - Get statistics about the current session

- **Artifact** - Data class representing a conversation artifact with name, path, type, content, size, modified timestamp
- **ConversationContext** - Data class containing conversation state including ID, task info, mode, and artifacts

## Operating Contracts

- Conversation detection scans `~/.gemini/antigravity/brain/` for directories with `.md` artifacts
- Artifact types are validated against: `task`, `implementation_plan`, `walkthrough`, `other`
- Tool invocation validates against the known TOOLS list (19 available tools)
- CLI messaging attempts `antigravity` or `agy` CLI before falling back to simulated tool invocation
- GUI automation uses AppleScript for direct keystroke input to the Antigravity application
- Events are emitted for: connected, disconnected, artifact_created, artifact_updated, artifact_deleted, conversation_switched

## Signposting

- **Parent Directory**: [ide/](../README.md) - IDE integrations module
- **Sibling Modules**:
  - [cursor/](../cursor/README.md) - Cursor IDE integration
  - [vscode/](../vscode/README.md) - VSCode integration
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
