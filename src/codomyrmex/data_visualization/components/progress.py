"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class ProgressBar(BaseComponent):
    """Progress bar component."""
    value: float = 0.0
    max_value: float = 100.0
    label: str = ""
