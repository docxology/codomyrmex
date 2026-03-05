"""Inter-agent messaging submodule.

Message passing, channel management, and communication patterns
for multi-agent collaboration.
"""

from .broadcaster import (
    Broadcaster,
    Subscription,
    TopicInfo,
)
from .channels import (
    Channel,
    ChannelInfo,
    ChannelManager,
    ChannelState,
    MessageQueue,
    QueueChannel,
)
from .direct import (
    ConversationTracker,
    DirectMessenger,
    PendingRequest,
)

__all__ = [
    "Broadcaster",
    "Channel",
    "ChannelInfo",
    "ChannelManager",
    # Channels
    "ChannelState",
    "ConversationTracker",
    "DirectMessenger",
    "MessageQueue",
    # Direct messaging
    "PendingRequest",
    "QueueChannel",
    # Broadcaster
    "Subscription",
    "TopicInfo",
]
