# Antigravity - Agent Coordination

## Purpose

Integration layer for Google DeepMind's Antigravity IDE, providing programmatic control, inter-agent messaging via JSONL relay, artifact management, and conversation tracking.

## Key Components

| Component | Role |
|-----------|------|
| `AntigravityClient` | `IDEClient` subclass: connect, execute commands, manage artifacts and conversations |
| `AgentRelay` | JSONL-backed inter-agent message bus at `~/.codomyrmex/agent_relay/<channel>/` |
| `RelayMessage` | Dataclass with message type constants: CHAT, TOOL_REQUEST, TOOL_RESULT, SYSTEM, HEARTBEAT |
| `Artifact` | Dataclass: name, path, artifact_type, content, size, modified |
| `ConversationContext` | Dataclass: conversation_id, task_name, task_status, mode, artifacts |
| `AntigravityToolProvider` | Tool provider bridge (lazy import) |
| `LiveAgentBridge` | Live agent communication bridge (lazy import) |
| `MessageScheduler` | Message scheduling for relay (lazy import) |

## Operating Contracts

- `AntigravityClient.connect()` checks for `~/.gemini/` directory presence.
- `send_chat_gui()` uses AppleScript automation on macOS; returns `False` on non-macOS platforms.
- Artifact storage location: `~/.gemini/antigravity/brain/`.
- `AgentRelay` stores messages as JSONL at `~/.codomyrmex/agent_relay/<channel_id>/messages.jsonl`.
- `await_response()` polls with configurable timeout and interval.
- 18 tool names and 4 artifact types are defined as class-level constants on `AntigravityClient`.

## Integration Points

- **Parent module**: `ide/` provides the `IDEClient` base class.
- **Event system**: `AgentRelay` can integrate with `events/` for cross-agent communication.
- **Lazy imports**: Bridge classes (`AntigravityToolProvider`, `LiveAgentBridge`, etc.) are imported on first access to reduce startup cost.

## Navigation

- **Parent**: [ide/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
