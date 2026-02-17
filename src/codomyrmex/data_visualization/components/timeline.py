"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class TimelineEvent(BaseComponent):
    """A single event in a timeline."""
    timestamp: str = ""
    label: str = ""
    description: str = ""

@dataclass
class Timeline(BaseComponent):
    """Timeline component."""
    events: list = field(default_factory=list)
