"""Component module."""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from ._base import BaseComponent


@dataclass
class JsonView(BaseComponent):
    """JSON viewer component."""
    data: dict = field(default_factory=dict)
    collapsed: bool = True
    label: str = ""

    def render(self) -> str:
        """Execute Render operations natively."""
        formatted = json.dumps(self.data, indent=2, default=str)
        open_attr = "" if self.collapsed else " open"
        title = self.label or "JSON"
        return (
            f'<details{open_attr}>'
            f'<summary>{title}</summary>'
            f'<pre><code>{formatted}</code></pre>'
            f'</details>'
        )

    def __str__(self) -> str:
        """Execute   Str   operations natively."""
        return self.render()
