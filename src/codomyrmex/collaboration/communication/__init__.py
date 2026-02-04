"""
Inter-agent messaging submodule.

Message passing, channel management, and communication patterns
for multi-agent collaboration.
"""

from .channels import (
    ChannelState,
    ChannelInfo,
    Channel,
    MessageQueue,
    QueueChannel,
    ChannelManager,
)
from .broadcaster import (
    Subscription,
    TopicInfo,
    Broadcaster,
)
from .direct import (
    PendingRequest,
    DirectMessenger,
    ConversationTracker,
)

__all__ = [
    # Channels
    "ChannelState",
    "ChannelInfo",
    "Channel",
    "MessageQueue",
    "QueueChannel",
    "ChannelManager",
    # Broadcaster
    "Subscription",
    "TopicInfo",
    "Broadcaster",
    # Direct messaging
    "PendingRequest",
    "DirectMessenger",
    "ConversationTracker",
]
