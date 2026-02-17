"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class HeatmapTable(BaseComponent):
    """Heatmap table component."""
    rows: list = field(default_factory=list)
    columns: list = field(default_factory=list)
    values: list = field(default_factory=list)
