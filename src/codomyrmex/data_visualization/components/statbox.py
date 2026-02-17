"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class StatBox(BaseComponent):
    """Stat box component."""
    label: str = ""
    value: str = ""
    delta: str = ""
