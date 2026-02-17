"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class ChatBubble(BaseComponent):
    """Chat bubble component."""
    message: str = ""
    role: str = "user"
    timestamp: str = ""
