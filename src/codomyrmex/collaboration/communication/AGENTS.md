# Codomyrmex Agents — src/codomyrmex/collaboration/communication

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides three communication patterns for inter-agent messaging: topic-based broadcast (`Broadcaster`), queue-backed point-to-point channels (`QueueChannel` via `ChannelManager`), and request-response direct messaging (`DirectMessenger`) with conversation tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `broadcaster.py` | `Broadcaster` | Topic-based pub/sub with subscription filters and retained message replay |
| `broadcaster.py` | `Subscription` | Dataclass binding subscriber ID, topic, handler, and optional filter |
| `broadcaster.py` | `TopicInfo` | Topic metadata: subscriber count, message count, created timestamp |
| `channels.py` | `Channel` | Abstract base for communication channels with open/close/pause lifecycle |
| `channels.py` | `ChannelState` | Enum: OPEN, CLOSED, PAUSED, ERROR |
| `channels.py` | `MessageQueue` | Async queue with optional max size and message TTL expiration |
| `channels.py` | `QueueChannel` | Concrete channel backed by `MessageQueue` |
| `channels.py` | `ChannelManager` | Factory and registry for channels with lifecycle management |
| `direct.py` | `DirectMessenger` | Point-to-point messaging with request-response via `asyncio.Future` |
| `direct.py` | `PendingRequest` | Tracks in-flight requests with timeout/expiration detection |
| `direct.py` | `ConversationTracker` | Groups related messages into named conversations per agent |

## Operating Contracts

- `Broadcaster.publish()` raises `ChannelError` if the topic does not exist; create topics first via `create_topic()` or let `subscribe()` auto-create.
- `DirectMessenger.send()` raises `MessageDeliveryError` if no handler is registered for the receiver.
- `MessageQueue.get()` respects `message_ttl`: expired messages are silently skipped and the next valid message is returned.
- `QueueChannel.send()` raises `ChannelError` when the channel state is not OPEN.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `collaboration.exceptions` (ChannelError, MessageDeliveryError), `collaboration.protocols` (AgentMessage, MessageType)
- **Used by**: `collaboration.agents` (CollaborativeAgent inbox), `collaboration.coordination`, `collaboration.swarm`

## Navigation

- **Parent**: [collaboration](../README.md)
- **Root**: [Root](../../../../README.md)
