"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class JsonView(BaseComponent):
    """JSON viewer component."""
    data: dict = field(default_factory=dict)
    collapsed: bool = True
