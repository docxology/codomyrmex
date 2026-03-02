# Inter-Agent Communication — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides broadcast, channel, and direct messaging primitives for inter-agent communication. All three patterns are async-compatible and use `AgentMessage` from the protocols submodule as the wire format.

## Architecture

Three independent subsystems: (1) `Broadcaster` for one-to-many pub/sub with topic-based routing and message retention, (2) `ChannelManager`/`QueueChannel` for point-to-point channel management backed by `asyncio.Queue`, and (3) `DirectMessenger` for request-response patterns using `asyncio.Future` completion.

## Key Classes

### `Broadcaster`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_topic` | `topic: str` | `None` | Initialize a topic with empty subscriber set |
| `subscribe` | `topic, subscriber_id, handler, filter_fn, replay_retained` | `str` | Returns subscription ID; auto-creates topic if missing |
| `publish` | `topic: str, message: AgentMessage` | `int` | Async delivery to all matching subscribers; returns delivery count |
| `publish_sync` | `topic: str, message: AgentMessage` | `int` | Sync variant; creates tasks for async handlers |
| `unsubscribe_all` | `subscriber_id: str` | `int` | Remove all subscriptions for an agent |

### `MessageQueue`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `put` | `message: AgentMessage, timeout: float` | `None` | Enqueue with optional timeout; raises `ChannelError` on full |
| `get` | `timeout: float` | `AgentMessage` | Dequeue with TTL-based expiration filtering |
| `clear` | — | `int` | Drain all messages; returns count cleared |

### `DirectMessenger`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `send` | `sender_id, receiver_id, content, metadata` | `None` | Fire-and-forget delivery to registered handler |
| `request` | `sender_id, receiver_id, content, timeout, metadata` | `Any` | Send and await response via Future |
| `respond` | `original_message, content, metadata` | `None` | Complete a pending request's Future |
| `get_message_log` | `agent_id: str, limit: int` | `list[AgentMessage]` | Filtered audit log, most recent first |

### `ConversationTracker`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start_conversation` | `participants: list[str], initial_message` | `str` | Returns conversation ID |
| `add_message` | `conversation_id: str, message: AgentMessage` | `None` | Appends to conversation |
| `get_agent_conversations` | `agent_id: str` | `list[str]` | Lists conversation IDs for an agent |

## Dependencies

- **Internal**: `collaboration.exceptions`, `collaboration.protocols`
- **External**: Standard library only (`asyncio`, `uuid`, `logging`, `datetime`)

## Constraints

- `Broadcaster` retains up to `retention_count` messages per topic (default 100) for replay.
- `MessageQueue` supports bounded (`max_size > 0`) and unbounded modes.
- `DirectMessenger` maintains a rolling log of up to 1000 messages.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ChannelError` raised on publish to non-existent topic, full queue, or closed channel.
- `MessageDeliveryError` raised when no handler registered for receiver or handler throws.
- `asyncio.TimeoutError` raised when request timeout expires.
- All errors logged before propagation.
