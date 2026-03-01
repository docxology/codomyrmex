"""AgentMailProvider mixins for modular method grouping.

Re-exports all four mixins so they can be imported from
``codomyrmex.email.agentmail.mixins`` directly.
"""

from .draft_mixin import DraftMixin
from .inbox_mixin import InboxMixin
from .thread_mixin import ThreadMixin
from .webhook_mixin import WebhookMixin

__all__ = [
    "DraftMixin",
    "InboxMixin",
    "ThreadMixin",
    "WebhookMixin",
]
