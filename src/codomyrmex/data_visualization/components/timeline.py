"""Component module."""
from dataclasses import dataclass, field

from ._base import BaseComponent


@dataclass
class TimelineEvent(BaseComponent):
    """A single event in a timeline."""
    timestamp: str = ""
    label: str = ""
    description: str = ""

    def render(self) -> str:
        """render ."""
        return (
            f'<div class="timeline-event">'
            f'<time>{self.timestamp}</time>'
            f'<h4>{self.label}</h4>'
            f'<p>{self.description}</p>'
            f'</div>'
        )

    def __str__(self) -> str:
        """str ."""
        return self.render()

@dataclass
class Timeline(BaseComponent):
    """Timeline component."""
    events: list = field(default_factory=list)

    def render(self) -> str:
        """render ."""
        inner = "\n".join(
            e.render() if hasattr(e, "render") else str(e) for e in self.events
        )
        return f'<div class="timeline">{inner}</div>'

    def __str__(self) -> str:
        """str ."""
        return self.render()
