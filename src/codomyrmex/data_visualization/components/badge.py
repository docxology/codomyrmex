"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class Badge(BaseComponent):
    """Badge component."""
    label: str = ""
    color: str = "#3B82F6"
