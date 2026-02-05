# collaboration/communication

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Inter-agent messaging submodule. Provides message passing, channel management, and communication patterns for multi-agent collaboration. Supports queue-based channels, topic-based publish/subscribe broadcasting, and direct request-response messaging with conversation tracking.

## Key Exports

### Channels

- **`ChannelState`** -- Channel lifecycle state enumeration
- **`ChannelInfo`** -- Channel metadata (name, state, message count)
- **`Channel`** -- Base channel abstraction
- **`MessageQueue`** -- Underlying message queue implementation
- **`QueueChannel`** -- Queue-backed channel for ordered message delivery
- **`ChannelManager`** -- Manages multiple channels; create, close, and route messages

### Broadcaster (Pub/Sub)

- **`Subscription`** -- Topic subscription with callback and filter
- **`TopicInfo`** -- Topic metadata (name, subscriber count)
- **`Broadcaster`** -- Publish/subscribe message broadcaster across topics

### Direct Messaging

- **`PendingRequest`** -- Pending request-response message awaiting reply
- **`DirectMessenger`** -- Point-to-point messaging between specific agents
- **`ConversationTracker`** -- Tracks multi-turn conversations between agent pairs

## Directory Contents

- `__init__.py` - Package init; re-exports from channels, broadcaster, and direct
- `channels.py` - Channel, QueueChannel, and ChannelManager
- `broadcaster.py` - Pub/sub Broadcaster and Subscription
- `direct.py` - DirectMessenger and ConversationTracker
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [collaboration](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
