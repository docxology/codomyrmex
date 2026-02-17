"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class Alert(BaseComponent):
    """Alert component."""
    message: str = ""
    level: str = "info"
