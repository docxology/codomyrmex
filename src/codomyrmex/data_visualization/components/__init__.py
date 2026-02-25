"""Visual components for data visualization dashboards.

Provides UI elements: TextBlock, CodeBlock, Image, Video, Badge,
Alert, ProgressBar, Timeline, TimelineEvent, StatBox, ChatBubble,
JsonView, HeatmapTable.
"""
from ._base import BaseComponent
from .alert import Alert
from .badge import Badge
from .chat_bubble import ChatBubble
from .heatmap_table import HeatmapTable
from .json_view import JsonView
from .media import Image, Video
from .progress import ProgressBar
from .statbox import StatBox
from .text import CodeBlock, TextBlock
from .timeline import Timeline, TimelineEvent

__all__ = [
    "BaseComponent",
    "Alert",
    "Badge",
    "ChatBubble",
    "CodeBlock",
    "HeatmapTable",
    "Image",
    "JsonView",
    "ProgressBar",
    "StatBox",
    "TextBlock",
    "Timeline",
    "TimelineEvent",
    "Video",
]
