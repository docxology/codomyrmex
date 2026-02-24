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

    def render(self) -> str:
        """Execute Render operations natively."""
        align = "right" if self.role == "user" else "left"
        label = self.role.capitalize()
        return (
            f'<div class="chat-bubble" style="float: {align}; '
            f'padding: 8px; margin: 4px; border-radius: 8px;">'
            f'<strong>{label}</strong>: {self.message}'
            f'<div class="timestamp">{self.timestamp}</div>'
            f'</div>'
        )

    def __str__(self) -> str:
        """Execute   Str   operations natively."""
        return self.render()
