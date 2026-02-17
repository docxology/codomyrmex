"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class Image(BaseComponent):
    """Image component."""
    src: str = ""
    alt: str = ""

@dataclass
class Video(BaseComponent):
    """Video component."""
    src: str = ""
    autoplay: bool = False
