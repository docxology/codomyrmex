"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class TextBlock(BaseComponent):
    """Text block component."""
    content: str = ""

@dataclass
class CodeBlock(BaseComponent):
    """Code block component."""
    code: str = ""
    language: str = "python"
