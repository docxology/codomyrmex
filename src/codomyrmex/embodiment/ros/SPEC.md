# ROS2 Bridge -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

In-process ROS2-style pub/sub message bridge for embodied agent communication. Provides typed topics, message history, latching (retained last message for late subscribers), and wildcard subscription support without requiring the `rclpy` runtime.

## Architecture

`ROS2Bridge` maintains per-topic subscriber lists, message history queues (bounded deques), and latched message state. Topics are created on demand during publish or subscribe. The design mirrors ROS2 topic semantics so the transport layer can be swapped to real ROS2 without changing the application API.

## Key Classes

### `Message` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `topic` | `str` | Topic name (e.g., "/odom") |
| `payload` | `dict[str, Any]` | Message content |
| `timestamp` | `float` | Unix timestamp (auto-populated) |
| `sender` | `str` | Node name of the publisher |

### `TopicInfo` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Topic name |
| `message_type` | `str` | Expected message type (default "dict") |
| `latched` | `bool` | Whether the last message is retained for late subscribers |
| `subscriber_count` | `int` | Number of active subscriptions |
| `total_published` | `int` | Cumulative message count |

### `ROS2Bridge`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `node_name, history_depth?` | -- | Initialize the bridge with a node name and history buffer size |
| `create_topic` | `topic, message_type?, latched?` | `None` | Register a topic (idempotent) |
| `list_topics` | -- | `list[TopicInfo]` | Return metadata for all registered topics |
| `publish` | `topic, payload` | `Message` | Publish a message; auto-creates topic if needed |
| `subscribe` | `topic, callback, replay_latched?` | `Callable[[], None]` | Subscribe to a topic; returns an unsubscribe callable |
| `get_history` | `topic, last_n?` | `list[Message]` | Return message history for a topic |
| `simulate_message` | `topic, payload` | `None` | Deliver a test message to subscribers without storing |
| `clear_history` | `topic?` | `None` | Clear history for one or all topics |

## Dependencies

- **Internal**: None
- **External**: None (Python stdlib: `collections.deque`, `logging`, `time`)

## Constraints

- Does not require `rclpy` -- runs entirely in-process for testing and simulation.
- History depth is bounded by `maxlen` on the deque (default 100 messages per topic).
- Subscriber callback exceptions are caught and logged but do not stop message delivery to other subscribers.
- Latched replay delivers the last published message to new subscribers immediately on subscription.
- Zero-mock: real message delivery only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Subscriber callback failures are caught via `logger.exception` and do not propagate.
- Unsubscribe on an already-removed callback logs a debug message and does not raise.
- All errors logged before propagation.
